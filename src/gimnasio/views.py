from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg
from .models import *
from .forms import RegistroForm
from datetime import datetime, timedelta

def es_profesor(user):
    return user.perfil.es_profesor if hasattr(user, 'perfil') else False

def index(request):
    return render(request, 'gimnasio/index.html')

# Vistas para Alumnos
@login_required
def perfil_alumno(request):
    if es_profesor(request.user):
        return redirect('gimnasio:panel_profesor')
    
    try:
        alumno = request.user.alumno
        rutinas = Rutina.objects.filter(alumno=alumno, activa=True)
        ejercicios_completados = EjercicioCompletado.objects.filter(
            alumno=alumno,
            fecha__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Obtener el último pago de cuota
        ultimo_pago = PagoCuota.objects.filter(alumno=alumno).order_by('-mes_correspondiente').first()
        cuota_al_dia = False
        if ultimo_pago:
            mes_actual = timezone.now().date().replace(day=1)
            cuota_al_dia = ultimo_pago.mes_correspondiente >= mes_actual
        
        # Obtener progreso
        registros_progreso = RegistroProgreso.objects.filter(
            alumno=alumno
        ).order_by('-fecha')[:10]
        
        context = {
            'alumno': alumno,
            'rutinas': rutinas,
            'ejercicios_completados': ejercicios_completados,
            'ultimo_pago': ultimo_pago,
            'cuota_al_dia': cuota_al_dia,
            'registros_progreso': registros_progreso
        }
        return render(request, 'gimnasio/perfil_alumno.html', context)
    except Alumno.DoesNotExist:
        return redirect('gimnasio:crear_perfil_alumno')

@login_required
def crear_perfil_alumno(request):
    if hasattr(request.user, 'alumno'):
        return redirect('gimnasio:perfil_alumno')
        
    if request.method == 'POST':
        try:
            # Crear perfil si no existe
            if not hasattr(request.user, 'perfil'):
                Perfil.objects.create(usuario=request.user, es_profesor=False)
            
            # Crear alumno
            alumno = Alumno.objects.create(
                usuario=request.user,
                nombre=request.POST.get('nombre') or request.user.username,
                edad=request.POST.get('edad'),
                altura=request.POST.get('altura'),
                peso=request.POST.get('peso'),
                horario=request.POST.get('horario', 'Mañana')
            )
            
            # Crear primer registro de progreso
            RegistroProgreso.objects.create(
                alumno=alumno,
                peso=request.POST.get('peso')
            )
            
            messages.success(request, '¡Perfil creado exitosamente!')
            return redirect('gimnasio:perfil_alumno')
        except Exception as e:
            messages.error(request, f'Error al crear el perfil: {str(e)}')
    
    return render(request, 'gimnasio/crear_perfil_alumno.html')

@login_required
def completar_ejercicio(request, detalle_rutina_id):
    detalle = get_object_or_404(DetalleRutina, id=detalle_rutina_id)
    if request.method == 'POST' and request.user == detalle.rutina.alumno.usuario:
        EjercicioCompletado.objects.create(
            alumno=request.user.alumno,
            detalle_rutina=detalle,
            series_completadas=request.POST.get('series_completadas'),
            peso_usado=request.POST.get('peso_usado'),
            notas=request.POST.get('notas', '')
        )
        messages.success(request, '¡Ejercicio completado!')
        return redirect('gimnasio:ver_rutina', rutina_id=detalle.rutina.id)
    return redirect('gimnasio:perfil_alumno')

@login_required
def registrar_progreso(request):
    if request.method == 'POST':
        try:
            RegistroProgreso.objects.create(
                alumno=request.user.alumno,
                peso=request.POST.get('peso'),
                notas=request.POST.get('notas', '')
            )
            messages.success(request, 'Progreso registrado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al registrar progreso: {str(e)}')
    return redirect('gimnasio:perfil_alumno')

# Vistas para Profesores
@login_required
@user_passes_test(es_profesor)
def panel_profesor(request):
    alumnos = Alumno.objects.all()
    alumnos_stats = []
    
    for alumno in alumnos:
        # Estadísticas de ejercicios completados último mes
        ejercicios_mes = EjercicioCompletado.objects.filter(
            alumno=alumno,
            fecha__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Último pago de cuota
        ultimo_pago = PagoCuota.objects.filter(alumno=alumno).order_by('-mes_correspondiente').first()
        
        # Rutinas activas
        rutinas_activas = Rutina.objects.filter(alumno=alumno, activa=True).count()
        
        alumnos_stats.append({
            'alumno': alumno,
            'ejercicios_mes': ejercicios_mes,
            'ultimo_pago': ultimo_pago,
            'rutinas_activas': rutinas_activas
        })
    
    context = {
        'alumnos_stats': alumnos_stats,
        'total_alumnos': len(alumnos),
        'alumnos_activos': sum(1 for stat in alumnos_stats if stat['ejercicios_mes'] > 0)
    }
    return render(request, 'gimnasio/panel_profesor.html', context)

@login_required
@user_passes_test(es_profesor)
def gestionar_rutina(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    if request.method == 'POST':
        # Desactivar rutinas anteriores
        Rutina.objects.filter(alumno=alumno, activa=True).update(activa=False)
        
        # Crear nueva rutina
        rutina = Rutina.objects.create(
            alumno=alumno,
            profesor=request.user
        )
        
        # Procesar ejercicios
        ejercicios = request.POST.getlist('ejercicios')
        for i, ej_id in enumerate(ejercicios):
            ejercicio = Ejercicio.objects.get(id=ej_id)
            DetalleRutina.objects.create(
                rutina=rutina,
                ejercicio=ejercicio,
                series=request.POST.get(f'series_{ej_id}'),
                repeticiones=request.POST.get(f'repeticiones_{ej_id}'),
                peso=request.POST.get(f'peso_{ej_id}'),
                orden=i
            )
        messages.success(request, 'Rutina creada exitosamente')
        return redirect('gimnasio:ver_rutina', rutina_id=rutina.id)
    
    categorias = CategoriaEjercicio.objects.all()
    context = {
        'alumno': alumno,
        'categorias': categorias,
        'rutinas_activas': Rutina.objects.filter(alumno=alumno, activa=True)
    }
    return render(request, 'gimnasio/gestionar_rutina.html', context)

@login_required
@user_passes_test(es_profesor)
def registrar_pago(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    if request.method == 'POST':
        try:
            PagoCuota.objects.create(
                alumno=alumno,
                fecha_pago=timezone.now().date(),
                monto=request.POST.get('monto'),
                mes_correspondiente=request.POST.get('mes_correspondiente'),
                comprobante=request.FILES.get('comprobante'),
                notas=request.POST.get('notas', '')
            )
            alumno.cuota_pagada = True
            alumno.save()
            messages.success(request, 'Pago registrado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al registrar pago: {str(e)}')
    return redirect('gimnasio:panel_profesor')

@login_required
def ver_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    if not es_profesor(request.user) and rutina.alumno.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver esta rutina')
        return redirect('gimnasio:perfil_alumno')
    
    detalles = rutina.detalles.all().order_by('orden')
    ejercicios_completados = {
        ej.detalle_rutina_id: ej 
        for ej in EjercicioCompletado.objects.filter(
            detalle_rutina__rutina=rutina,
            fecha__gte=timezone.now().date()
        )
    }
    
    context = {
        'rutina': rutina,
        'detalles': detalles,
        'ejercicios_completados': ejercicios_completados,
        'es_profesor': es_profesor(request.user)
    }
    return render(request, 'gimnasio/ver_rutina.html', context)

def registro(request):
    if request.user.is_authenticated:
        return redirect('gimnasio:index')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil de usuario
            Perfil.objects.create(usuario=user, es_profesor=False)
            # Iniciar sesión
            login(request, user)
            messages.success(request, '¡Registro exitoso! Por favor, completa tu perfil.')
            return redirect('gimnasio:crear_perfil_alumno')
    else:
        form = RegistroForm()
    
    return render(request, 'gimnasio/registro.html', {'form': form})

@login_required
def perfil(request):
    context = {}
    
    # Verificar si el usuario es profesor
    if es_profesor(request.user):
        return redirect('gimnasio:panel_profesor')
    
    # Intentar obtener el perfil de alumno
    try:
        alumno = request.user.alumno
        rutinas = Rutina.objects.filter(alumno=alumno)
        context['alumno'] = alumno
        context['rutinas'] = rutinas
        return render(request, 'gimnasio/perfil.html', context)
    except Alumno.DoesNotExist:
        if request.method == 'POST':
            try:
                alumno = Alumno.objects.create(
                    usuario=request.user,
                    nombre=request.user.get_full_name() or request.user.username,
                    edad=request.POST.get('edad'),
                    altura=request.POST.get('altura'),
                    peso=request.POST.get('peso'),
                    horario=request.POST.get('horario')
                )
                messages.success(request, 'Perfil creado exitosamente')
                return redirect('gimnasio:perfil')
            except Exception as e:
                messages.error(request, f'Error al crear el perfil: {str(e)}')
        return render(request, 'gimnasio/crear_perfil.html')

@login_required
@user_passes_test(es_profesor)
def asignar_rutina(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    if request.method == 'POST':
        rutina = Rutina.objects.create(
            alumno=alumno,
            profesor=request.user
        )
        # Procesar ejercicios seleccionados
        ejercicios = request.POST.getlist('ejercicios')
        for ej_id in ejercicios:
            ejercicio = Ejercicio.objects.get(id=ej_id)
            DetalleRutina.objects.create(
                rutina=rutina,
                ejercicio=ejercicio,
                series=request.POST.get(f'series_{ej_id}'),
                repeticiones=request.POST.get(f'repeticiones_{ej_id}'),
                peso=request.POST.get(f'peso_{ej_id}')
            )
        messages.success(request, 'Rutina asignada correctamente')
        return redirect('gimnasio:panel_profesor')
    
    categorias = CategoriaEjercicio.objects.all()
    ejercicios = Ejercicio.objects.all()
    return render(request, 'gimnasio/asignar_rutina.html', {
        'alumno': alumno,
        'categorias': categorias,
        'ejercicios': ejercicios
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return render(request, 'gimnasio/logout.html')
