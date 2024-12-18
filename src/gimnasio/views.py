from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg
from .models import *
from .forms import RegistroForm, RutinaForm, RutinaEjercicioForm, EjercicioCompletadoForm, AlumnoForm
from datetime import datetime, timedelta
from django.http import JsonResponse

def es_profesor(user):
    if not user.is_authenticated:
        return False
    try:
        return user.perfil.es_profesor
    except:
        return False

def index(request):
    return render(request, 'gimnasio/index.html')

# Vistas para Alumnos
@login_required
def perfil_alumno(request):
    try:
        alumno = Alumno.objects.get(usuario=request.user)
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
        messages.warning(request, 'Primero debes completar tu perfil de alumno.')
        return redirect('gimnasio:crear_perfil_alumno')

@login_required
def crear_perfil_alumno(request):
    try:
        # Verificar si ya existe un perfil de alumno
        alumno = Alumno.objects.get(usuario=request.user)
        messages.info(request, 'Ya tienes un perfil de alumno.')
        return redirect('gimnasio:perfil_alumno')
    except Alumno.DoesNotExist:
        if request.method == 'POST':
            form = AlumnoForm(request.POST)
            if form.is_valid():
                alumno = form.save(commit=False)
                alumno.usuario = request.user
                alumno.save()
                # Guardar los días de asistencia después de crear el alumno
                form.save_m2m()
                messages.success(request, '¡Perfil creado exitosamente!')
                return redirect('gimnasio:perfil_alumno')
        else:
            form = AlumnoForm()
        
        return render(request, 'gimnasio/crear_perfil.html', {'form': form})

@login_required
def completar_ejercicio(request, rutina_ejercicio_id):
    rutina_ejercicio = get_object_or_404(RutinaEjercicio, id=rutina_ejercicio_id)
    if request.method == 'POST' and request.user == rutina_ejercicio.rutina.alumno.usuario:
        EjercicioCompletado.objects.create(
            alumno=request.user.alumno,
            rutina_ejercicio=rutina_ejercicio,
            series_completadas=request.POST.get('series_completadas'),
            peso_usado=request.POST.get('peso_usado'),
            notas=request.POST.get('notas', '')
        )
        messages.success(request, '¡Ejercicio completado!')
        return redirect('gimnasio:ver_rutina', rutina_id=rutina_ejercicio.rutina.id)
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
    # Estadísticas generales
    total_alumnos = Alumno.objects.filter(rutinas__profesor=request.user).distinct().count()
    rutinas_activas = Rutina.objects.filter(profesor=request.user, activa=True).count()
    ejercicios_hoy = EjercicioCompletado.objects.filter(
        rutina_ejercicio__rutina__profesor=request.user,
        fecha__date=timezone.now().date()
    ).count()
    
    # Obtener alumnos con su información
    alumnos = Alumno.objects.filter(rutinas__profesor=request.user).distinct()
    
    # Ordenar alumnos según el parámetro
    orden = request.GET.get('orden', 'nombre')
    if orden == 'nombre':
        alumnos = alumnos.order_by('nombre')
    elif orden == 'fecha':
        alumnos = alumnos.order_by('-usuario__date_joined')
    
    context = {
        'total_alumnos': total_alumnos,
        'rutinas_activas': rutinas_activas,
        'ejercicios_hoy': ejercicios_hoy,
        'alumnos': alumnos,
    }
    return render(request, 'gimnasio/panel_profesor.html', context)

@login_required
@user_passes_test(es_profesor)
def ver_alumnos(request):
    alumnos = Alumno.objects.filter(profesor=request.user, activo=True).order_by('nombre')
    return render(request, 'gimnasio/ver_alumnos.html', {'alumnos': alumnos})

@login_required
@user_passes_test(es_profesor)
def asignar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.profesor = request.user
    alumno.save()
    messages.success(request, f'El alumno {alumno.nombre} ha sido asignado a tu lista.')
    return redirect('gimnasio:ver_alumnos')

@login_required
@user_passes_test(es_profesor)
def crear_rutina(request):
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        ejercicio_forms = []
        
        # Procesar los datos de ejercicios
        ejercicios_data = []
        for key in request.POST:
            if key.startswith('nombre_ejercicio-'):
                index = key.split('-')[1]
                ejercicio_data = {
                    'grupo_muscular': request.POST.get(f'grupo_muscular-{index}'),
                    'nombre_ejercicio': request.POST.get(f'nombre_ejercicio-{index}'),
                    'series': request.POST.get(f'series-{index}'),
                    'repeticiones': request.POST.get(f'repeticiones-{index}'),
                    'peso': request.POST.get(f'peso-{index}'),
                }
                ejercicios_data.append(ejercicio_data)
        
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.profesor = request.user
            rutina.save()
            
            # Guardar los ejercicios
            for i, ejercicio_data in enumerate(ejercicios_data, start=1):
                # Crear o obtener el ejercicio
                ejercicio, _ = Ejercicio.objects.get_or_create(
                    nombre=ejercicio_data['nombre_ejercicio'],
                    grupo_muscular=ejercicio_data['grupo_muscular'],
                    defaults={
                        'descripcion': '',
                        'creado_por': request.user
                    }
                )
                
                # Crear la relación RutinaEjercicio
                RutinaEjercicio.objects.create(
                    rutina=rutina,
                    ejercicio=ejercicio,
                    series=ejercicio_data['series'],
                    repeticiones=ejercicio_data['repeticiones'],
                    peso=ejercicio_data['peso'],
                    orden=i
                )
            
            messages.success(request, 'Rutina creada exitosamente')
            return redirect('gimnasio:panel_profesor')
    else:
        form = RutinaForm()
        ejercicio_form = RutinaEjercicioForm()
    
    context = {
        'form': form,
        'ejercicio_form': ejercicio_form,
    }
    return render(request, 'gimnasio/crear_rutina.html', context)

@login_required
@user_passes_test(es_profesor)
def crear_rutina_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        ejercicio_forms = []
        
        # Procesar los datos de ejercicios
        ejercicios_data = []
        for key in request.POST:
            if key.startswith('nombre_ejercicio-'):
                index = key.split('-')[1]
                ejercicio_data = {
                    'grupo_muscular': request.POST.get(f'grupo_muscular-{index}'),
                    'nombre_ejercicio': request.POST.get(f'nombre_ejercicio-{index}'),
                    'series': request.POST.get(f'series-{index}'),
                    'repeticiones': request.POST.get(f'repeticiones-{index}'),
                    'peso': request.POST.get(f'peso-{index}'),
                }
                ejercicios_data.append(ejercicio_data)
        
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.profesor = request.user
            rutina.alumno = alumno
            rutina.save()
            
            # Guardar los ejercicios
            for i, ejercicio_data in enumerate(ejercicios_data, start=1):
                # Crear o obtener el ejercicio
                ejercicio, _ = Ejercicio.objects.get_or_create(
                    nombre=ejercicio_data['nombre_ejercicio'],
                    grupo_muscular=ejercicio_data['grupo_muscular'],
                    defaults={
                        'descripcion': '',
                        'creado_por': request.user
                    }
                )
                
                # Crear la relación RutinaEjercicio
                RutinaEjercicio.objects.create(
                    rutina=rutina,
                    ejercicio=ejercicio,
                    series=ejercicio_data['series'],
                    repeticiones=ejercicio_data['repeticiones'],
                    peso=ejercicio_data['peso'],
                    orden=i
                )
            
            messages.success(request, f'Rutina creada exitosamente para {alumno.nombre}')
            return redirect('gimnasio:panel_profesor')
    else:
        form = RutinaForm(initial={'alumno': alumno})
        ejercicio_form = RutinaEjercicioForm()
    
    context = {
        'form': form,
        'ejercicio_form': ejercicio_form,
        'alumno': alumno,
    }
    return render(request, 'gimnasio/crear_rutina.html', context)

@login_required
@user_passes_test(es_profesor)
def gestionar_rutina(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    rutinas = Rutina.objects.filter(alumno=alumno).order_by('-fecha_creacion')
    
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.alumno = alumno
            rutina.profesor = request.user
            rutina.save()
            messages.success(request, 'Rutina creada exitosamente')
            return redirect('gimnasio:agregar_ejercicios_rutina', rutina_id=rutina.id)
    else:
        form = RutinaForm()
    
    context = {
        'alumno': alumno,
        'rutinas': rutinas,
        'form': form,
    }
    return render(request, 'gimnasio/gestionar_rutinas.html', context)

@login_required
@user_passes_test(es_profesor)
def ver_progreso(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    registros = RegistroProgreso.objects.filter(alumno=alumno).order_by('-fecha')
    ejercicios = EjercicioCompletado.objects.filter(alumno=alumno).order_by('-fecha')
    
    context = {
        'alumno': alumno,
        'registros': registros,
        'ejercicios': ejercicios,
    }
    return render(request, 'gimnasio/ver_progreso.html', context)

@login_required
@user_passes_test(es_profesor)
def gestionar_horario(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if request.method == 'POST':
        dias = request.POST.getlist('dias')
        horario = request.POST.get('horario')
        
        # Actualizar días de asistencia
        alumno.dias_asistencia.clear()
        for dia_id in dias:
            dia = DiaAsistencia.objects.get(id=dia_id)
            alumno.dias_asistencia.add(dia)
        
        # Actualizar horario
        alumno.horario = horario
        alumno.save()
        
        messages.success(request, 'Horario actualizado exitosamente')
        return redirect('gimnasio:ver_alumnos')
    
    context = {
        'alumno': alumno,
        'dias_disponibles': DiaAsistencia.objects.all(),
        'horarios': [('Mañana', 'Mañana'), ('Tarde', 'Tarde'), ('Noche', 'Noche')],
    }
    return render(request, 'gimnasio/gestionar_horario.html', context)

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
    
    detalles = rutina.ejercicios.through.objects.filter(rutina=rutina).order_by('orden')
    ejercicios_completados = {
        ej.rutina_ejercicio_id: ej 
        for ej in EjercicioCompletado.objects.filter(
            rutina_ejercicio__rutina=rutina,
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

@login_required
@user_passes_test(es_profesor)
def agregar_ejercicios_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    
    if request.method == 'POST':
        form = RutinaEjercicioForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.rutina = rutina
            detalle.save()
            messages.success(request, 'Ejercicio agregado a la rutina.')
            return redirect('gimnasio:agregar_ejercicios_rutina', rutina_id=rutina.id)
    else:
        form = RutinaEjercicioForm()
    
    ejercicios_actuales = rutina.ejercicios.through.objects.filter(rutina=rutina).order_by('orden')
    
    return render(request, 'gimnasio/rutinas/agregar_ejercicios.html', {
        'form': form,
        'rutina': rutina,
        'ejercicios': ejercicios_actuales
    })

@login_required
def ver_mis_rutinas(request):
    try:
        perfil = request.user.perfil
        if perfil.es_profesor:
            return redirect('gimnasio:panel_profesor')
        
        try:
            alumno = Alumno.objects.get(usuario=request.user)
            rutinas = Rutina.objects.filter(alumno=alumno, activa=True)
            return render(request, 'gimnasio/mis_rutinas.html', {
                'rutinas': rutinas,
                'alumno': alumno
            })
        except Alumno.DoesNotExist:
            messages.warning(request, 'Primero debes completar tu perfil de alumno.')
            return redirect('gimnasio:crear_perfil_alumno')
            
    except Perfil.DoesNotExist:
        # Si el usuario no tiene perfil, crearlo
        Perfil.objects.create(usuario=request.user, es_profesor=False)
        return redirect('gimnasio:crear_perfil_alumno')

@login_required
def detalle_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    
    # Verificar que el usuario tenga acceso a esta rutina
    if not (es_profesor(request.user) or request.user.alumno == rutina.alumno):
        messages.error(request, 'No tienes permiso para ver esta rutina.')
        return redirect('gimnasio:index')
    
    ejercicios = rutina.ejercicios.through.objects.filter(rutina=rutina).order_by('orden')
    
    return render(request, 'gimnasio/rutinas/detalle_rutina.html', {
        'rutina': rutina,
        'ejercicios': ejercicios
    })

@login_required
def registrar_ejercicio_completado(request, rutina_ejercicio_id):
    rutina_ejercicio = get_object_or_404(RutinaEjercicio, id=rutina_ejercicio_id)
    
    if request.method == 'POST':
        form = EjercicioCompletadoForm(request.POST)
        if form.is_valid():
            ejercicio_completado = form.save(commit=False)
            ejercicio_completado.alumno = request.user.alumno
            ejercicio_completado.rutina_ejercicio = rutina_ejercicio
            ejercicio_completado.save()
            messages.success(request, '¡Ejercicio registrado como completado!')
            return redirect('gimnasio:detalle_rutina', rutina_id=rutina_ejercicio.rutina.id)
    else:
        form = EjercicioCompletadoForm()
    
    return render(request, 'gimnasio/rutinas/registrar_ejercicio.html', {
        'form': form,
        'rutina_ejercicio': rutina_ejercicio
    })

def registro(request):
    if request.user.is_authenticated:
        return redirect('gimnasio:index')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil por defecto
            Perfil.objects.create(usuario=user, es_profesor=False)
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
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
def perfil_profesor(request):
    if not es_profesor(request.user):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('gimnasio:index')
    
    try:
        perfil = request.user.perfil
        if not perfil.es_profesor:
            messages.error(request, "Tu cuenta no está configurada como profesor.")
            return redirect('gimnasio:index')
            
        # Obtener estadísticas del profesor
        rutinas = Rutina.objects.filter(profesor=request.user)
        alumnos = Alumno.objects.filter(rutinas__profesor=request.user).distinct()
        
        context = {
            'perfil': perfil,
            'rutinas': rutinas,
            'alumnos': alumnos,
            'total_rutinas': rutinas.count(),
            'total_alumnos': alumnos.count(),
        }
        
        return render(request, 'gimnasio/perfil_profesor.html', context)
        
    except Exception as e:
        messages.error(request, "Hubo un error al cargar tu perfil de profesor.")
        return redirect('gimnasio:index')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('gimnasio:index')

def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, '¡Bienvenido de nuevo!')
            
            # Redirigir según el tipo de usuario
            if hasattr(user, 'perfil') and user.perfil.es_profesor:
                return redirect('gimnasio:panel_profesor')
            return redirect('gimnasio:perfil_alumno')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'gimnasio/iniciar_sesion.html')

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
            RutinaEjercicio.objects.create(
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
@user_passes_test(es_profesor)
def gestionar_ejercicios(request):
    ejercicios = Ejercicio.objects.filter(creado_por=request.user)
    
    if request.method == 'POST':
        # Crear nuevo ejercicio
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        grupo_muscular = request.POST.get('grupo_muscular')
        imagen_url = request.POST.get('imagen_url')
        video_url = request.POST.get('video_url')
        
        if nombre and descripcion and grupo_muscular:
            ejercicio = Ejercicio.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                grupo_muscular=grupo_muscular,
                imagen_url=imagen_url,
                video_url=video_url,
                creado_por=request.user
            )
            messages.success(request, 'Ejercicio creado exitosamente.')
            return redirect('gimnasio:gestionar_ejercicios')
        else:
            messages.error(request, 'Por favor complete todos los campos requeridos.')
    
    # Agrupar ejercicios por grupo muscular
    ejercicios_por_grupo = {}
    for ejercicio in ejercicios:
        if ejercicio.grupo_muscular not in ejercicios_por_grupo:
            ejercicios_por_grupo[ejercicio.grupo_muscular] = []
        ejercicios_por_grupo[ejercicio.grupo_muscular].append(ejercicio)
    
    context = {
        'ejercicios_por_grupo': ejercicios_por_grupo,
        'grupos_musculares': [
            'Pecho', 'Espalda', 'Hombros', 'Bíceps', 'Tríceps',
            'Piernas', 'Abdominales', 'Cardio', 'Otro'
        ]
    }
    
    return render(request, 'gimnasio/gestionar_ejercicios.html', context)

@login_required
@user_passes_test(es_profesor)
def editar_ejercicio(request, ejercicio_id):
    ejercicio = get_object_or_404(Ejercicio, id=ejercicio_id, creado_por=request.user)
    
    if request.method == 'POST':
        ejercicio.nombre = request.POST.get('nombre', ejercicio.nombre)
        ejercicio.descripcion = request.POST.get('descripcion', ejercicio.descripcion)
        ejercicio.grupo_muscular = request.POST.get('grupo_muscular', ejercicio.grupo_muscular)
        ejercicio.imagen_url = request.POST.get('imagen_url', ejercicio.imagen_url)
        ejercicio.video_url = request.POST.get('video_url', ejercicio.video_url)
        ejercicio.save()
        
        messages.success(request, 'Ejercicio actualizado exitosamente.')
        return redirect('gimnasio:gestionar_ejercicios')
    
    context = {
        'ejercicio': ejercicio,
        'grupos_musculares': [
            'Pecho', 'Espalda', 'Hombros', 'Bíceps', 'Tríceps',
            'Piernas', 'Abdominales', 'Cardio', 'Otro'
        ]
    }
    
    return render(request, 'gimnasio/editar_ejercicio.html', context)

@login_required
@user_passes_test(es_profesor)
def eliminar_ejercicio(request, ejercicio_id):
    ejercicio = get_object_or_404(Ejercicio, id=ejercicio_id, creado_por=request.user)
    
    if request.method == 'POST':
        ejercicio.delete()
        messages.success(request, 'Ejercicio eliminado exitosamente.')
        return redirect('gimnasio:gestionar_ejercicios')
    
    return render(request, 'gimnasio/eliminar_ejercicio.html', {'ejercicio': ejercicio})

@login_required
@user_passes_test(es_profesor)
def activar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id, profesor=request.user)
    rutina.activa = True
    rutina.save()
    messages.success(request, f'La rutina {rutina.nombre} ha sido activada.')
    return redirect('gimnasio:gestionar_rutina', alumno_id=rutina.alumno.id)

@login_required
@user_passes_test(es_profesor)
def desactivar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id, profesor=request.user)
    rutina.activa = False
    rutina.save()
    messages.success(request, f'La rutina {rutina.nombre} ha sido desactivada.')
    return redirect('gimnasio:gestionar_rutina', alumno_id=rutina.alumno.id)

@login_required
def get_ejercicios_por_grupo(request):
    grupo_muscular = request.GET.get('grupo_muscular')
    ejercicios = Ejercicio.objects.filter(grupo_muscular=grupo_muscular).values('id', 'nombre')
    return JsonResponse(list(ejercicios), safe=False)
