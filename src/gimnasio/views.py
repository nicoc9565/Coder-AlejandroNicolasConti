from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from .models import *
from .forms import RegistroForm, RutinaForm, RutinaEjercicioForm, EjercicioCompletadoForm, AlumnoForm, PagoCuotaForm
from django.http import JsonResponse

def es_profesor(user):
    """Verifica si el usuario es profesor o superusuario."""
    if user.is_superuser:
        return True
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.es_profesor

def index(request):
    """Vista principal de la aplicación."""
    return render(request, 'gimnasio/index.html')

def iniciar_sesion(request):
    """Maneja el inicio de sesión de usuarios."""
    if request.user.is_authenticated:
        return redirect('gimnasio:index')
    
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
    
    return render(request, 'gimnasio/login.html')

def registro(request):
    """Maneja el registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('gimnasio:index')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.create(usuario=user, es_profesor=False)
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('gimnasio:crear_perfil_alumno')
    else:
        form = RegistroForm()
    
    return render(request, 'gimnasio/registro.html', {'form': form})

@login_required
def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('gimnasio:index')

@login_required
def perfil(request):
    """Muestra el perfil del usuario."""
    if es_profesor(request.user):
        return redirect('gimnasio:panel_profesor')
    
    try:
        alumno = request.user.alumno
        rutinas = Rutina.objects.filter(alumno=alumno).select_related('profesor')
        return render(request, 'gimnasio/perfil.html', {
            'alumno': alumno,
            'rutinas': rutinas
        })
    except Alumno.DoesNotExist:
        messages.warning(request, 'Primero debes completar tu perfil de alumno.')
        return redirect('gimnasio:crear_perfil_alumno')

@login_required
def perfil_alumno(request):
    """Muestra el perfil detallado del alumno con sus rutinas y progreso."""
    try:
        # Obtener alumno con sus relaciones en una sola consulta
        alumno = Alumno.objects.select_related(
            'usuario', 'profesor'
        ).prefetch_related(
            'rutinas',
            'pagos',
            'registros_progreso'
        ).get(usuario=request.user)

        # Obtener rutinas activas
        rutinas = alumno.rutinas.filter(
            activa=True
        ).select_related('profesor').prefetch_related('ejercicios')

        # Obtener ejercicios completados recientes
        ejercicios_completados = EjercicioCompletado.objects.filter(
            alumno=alumno,
            fecha__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()

        # Obtener último pago y estado de cuota
        ultimo_pago = alumno.pagos.order_by('-mes_correspondiente').first()
        cuota_al_dia = False
        if ultimo_pago:
            mes_actual = timezone.now().date().replace(day=1)
            cuota_al_dia = ultimo_pago.mes_correspondiente >= mes_actual

        # Obtener registros de progreso recientes
        registros_progreso = alumno.registros_progreso.order_by('-fecha')[:10]

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
    """Crea un nuevo perfil de alumno."""
    try:
        alumno = Alumno.objects.get(usuario=request.user)
        messages.info(request, 'Ya tienes un perfil de alumno.')
        return redirect('gimnasio:perfil_alumno')
    except Alumno.DoesNotExist:
        if request.method == 'POST':
            form = AlumnoForm(request.POST)
            if form.is_valid():
                alumno = form.save(commit=False)
                alumno.usuario = request.user
                alumno.nombre = request.user.get_full_name() or request.user.username
                alumno.save()
                form.save_m2m()  # Guardar relaciones many-to-many
                messages.success(request, '¡Perfil creado exitosamente!')
                return redirect('gimnasio:perfil_alumno')
        else:
            form = AlumnoForm()
        
        return render(request, 'gimnasio/crear_perfil.html', {'form': form})

@login_required
def registrar_progreso(request):
    """Registra el progreso del alumno."""
    if request.method == 'POST':
        try:
            alumno = request.user.alumno
            RegistroProgreso.objects.create(
                alumno=alumno,
                peso=request.POST.get('peso'),
                notas=request.POST.get('notas', '')
            )
            messages.success(request, 'Progreso registrado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al registrar progreso: {str(e)}')
    return redirect('gimnasio:perfil_alumno')

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
@user_passes_test(es_profesor)
def panel_profesor(request):
    """Panel principal del profesor con resumen de alumnos y rutinas."""
    try:
        # Obtener parámetros de filtrado y ordenamiento
        orden = request.GET.get('orden', 'nombre')
        
        # Consulta base de alumnos
        alumnos_query = Alumno.objects.all() if request.user.is_superuser else Alumno.objects.filter(profesor=request.user)
        alumnos = alumnos_query.filter(
            activo=True
        ).select_related('usuario').prefetch_related('dias_asistencia')
        
        # Aplicar ordenamiento a alumnos
        if orden == 'nombre':
            alumnos = alumnos.order_by('nombre')
        elif orden == 'fecha':
            alumnos = alumnos.order_by('-fecha_registro')
        
        # Obtener rutinas activas
        rutinas_query = Rutina.objects.all() if request.user.is_superuser else Rutina.objects.filter(profesor=request.user)
        rutinas_activas = rutinas_query.filter(
            activa=True
        ).select_related(
            'alumno',
            'profesor'
        ).prefetch_related(
            'rutinaejercicio_set',
            'rutinaejercicio_set__ejercicio'
        ).order_by('-fecha_creacion')

        rutinas_procesadas = []
        for rutina in rutinas_activas:
            rutinas_procesadas.append({
                'id': rutina.id,
                'nombre': rutina.nombre,
                'alumno_nombre': rutina.alumno.nombre,
                'ejercicios_count': rutina.rutinaejercicio_set.count(),
                'fecha_creacion': rutina.fecha_creacion
            })
        
        ejercicios_query = EjercicioCompletado.objects
        if not request.user.is_superuser:
            ejercicios_query = ejercicios_query.filter(alumno__profesor=request.user)
        ejercicios_hoy = ejercicios_query.filter(
            fecha__date=timezone.now().date()
        ).count()
        
        total_alumnos = alumnos.count()
        
        context = {
            'alumnos': alumnos,
            'rutinas_activas': rutinas_procesadas,
            'estadisticas': {
                'total_alumnos': total_alumnos,
                'rutinas_activas': len(rutinas_procesadas),
                'ejercicios_hoy': ejercicios_hoy
            }
        }
        
        return render(request, 'gimnasio/panel_profesor.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar el panel: {str(e)}')
        return redirect('gimnasio:index')
        
@login_required
@user_passes_test(es_profesor)
def ver_alumnos(request):
    """Lista detallada de alumnos del profesor."""
    alumnos = Alumno.objects.filter(
        profesor=request.user, 
        activo=True
    ).select_related(
        'usuario'
    ).prefetch_related(
        'rutinas',
        'dias_asistencia'
    ).order_by('nombre')
    
    return render(request, 'gimnasio/ver_alumnos.html', {'alumnos': alumnos})

@login_required
@user_passes_test(es_profesor)
def asignar_alumno(request, alumno_id):
    """Asigna un alumno al profesor."""
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if alumno.profesor and alumno.profesor != request.user:
        messages.error(request, 'Este alumno ya está asignado a otro profesor.')
        return redirect('gimnasio:ver_alumnos')
    
    alumno.profesor = request.user
    alumno.save()
    messages.success(request, f'El alumno {alumno.nombre} ha sido asignado a tu lista.')
    return redirect('gimnasio:ver_alumnos')

@login_required
@user_passes_test(es_profesor)
def ver_progreso(request, alumno_id):
    """Muestra el progreso detallado de un alumno."""
    alumno = get_object_or_404(
        Alumno.objects.select_related('usuario'),
        id=alumno_id,
        profesor=request.user
    )
    
    # Obtener registros de progreso y ejercicios completados
    registros = RegistroProgreso.objects.filter(
        alumno=alumno
    ).select_related(
        'alumno'
    ).order_by('-fecha')
    
    ejercicios = EjercicioCompletado.objects.filter(
        alumno=alumno
    ).select_related(
        'rutina_ejercicio',
        'rutina_ejercicio__ejercicio'
    ).order_by('-fecha')
    
    context = {
        'alumno': alumno,
        'registros': registros,
        'ejercicios': ejercicios,
    }
    return render(request, 'gimnasio/ver_progreso.html', context)

@login_required
@user_passes_test(es_profesor)
def crear_rutina(request):
    """Crea una nueva rutina para un alumno."""
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        if form.is_valid():
            try:
                # Crear la rutina
                rutina = form.save(commit=False)
                if not request.user.is_superuser:
                    rutina.profesor = request.user
                rutina.save()
                form.save_m2m()
                
                messages.success(request, 'Rutina creada exitosamente')
                return redirect('gimnasio:ver_rutina', rutina_id=rutina.id)
            except Exception as e:
                messages.error(request, f'Error al crear la rutina: {str(e)}')
                return redirect('gimnasio:panel_profesor')
    else:
        # Filtrar alumnos según el tipo de usuario
        form = RutinaForm()
        if not request.user.is_superuser:
            form.fields['alumno'].queryset = Alumno.objects.filter(
                profesor=request.user,
                activo=True
            ).select_related('usuario')
        else:
            form.fields['alumno'].queryset = Alumno.objects.filter(
                activo=True
            ).select_related('usuario')

    return render(request, 'gimnasio/crear_rutina.html', {'form': form})

@login_required
@user_passes_test(es_profesor)
def ver_rutina(request, rutina_id):
    """Muestra los detalles de una rutina específica."""
    try:
        # Obtener la rutina con todas sus relaciones
        rutina_query = Rutina.objects
        if not request.user.is_superuser:
            rutina_query = rutina_query.filter(profesor=request.user)
            
        rutina = get_object_or_404(
            rutina_query.select_related(
                'profesor',
                'alumno'
            ).prefetch_related(
                'ejercicios',
                'rutinaejercicio_set__ejercicio'
            ),
            id=rutina_id
        )
        
        # Obtener ejercicios completados para esta rutina
        ejercicios_completados = EjercicioCompletado.objects.filter(
            rutina_ejercicio__rutina=rutina
        ).select_related(
            'rutina_ejercicio',
            'rutina_ejercicio__ejercicio'
        ).order_by('-fecha')
        
        context = {
            'rutina': rutina,
            'ejercicios': rutina.rutinaejercicio_set.all(),
            'ejercicios_completados': ejercicios_completados,
            'is_superuser': request.user.is_superuser
        }
        
        return render(request, 'gimnasio/ver_rutina.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar la rutina: {str(e)}')
        return redirect('gimnasio:panel_profesor')

@login_required
@user_passes_test(es_profesor)
def desactivar_rutina(request, rutina_id):
    """Desactiva una rutina existente."""
    try:
        # Obtener la rutina según el tipo de usuario
        rutina_query = Rutina.objects
        if not request.user.is_superuser:
            rutina_query = rutina_query.filter(profesor=request.user)
            
        rutina = get_object_or_404(rutina_query, id=rutina_id)
        rutina.activa = False
        rutina.save()
        
        messages.success(request, f'La rutina "{rutina.nombre}" ha sido desactivada.')
    except Exception as e:
        messages.error(request, f'Error al desactivar la rutina: {str(e)}')
    
    return redirect('gimnasio:panel_profesor')

@login_required
def registrar_pago(request, alumno_id=None):
    if not request.user.perfil.es_profesor:
        messages.error(request, "No tienes permisos para registrar pagos.")
        return redirect('gimnasio:index')
    
    alumno = None
    if alumno_id:
        try:
            alumno = Alumno.objects.get(id=alumno_id)
        except Alumno.DoesNotExist:
            messages.error(request, "El alumno especificado no existe.")
            return redirect('gimnasio:lista_pagos')
    
    if request.method == 'POST':
        form = PagoCuotaForm(request.POST)
        print("Form data:", request.POST)  
        if form.is_valid():
            try:
                if alumno_id:
                    form.instance.alumno = alumno
                
                pago = form.save()
                messages.success(request, f"Pago registrado exitosamente para {pago.alumno.nombre}")
                
                if alumno_id:
                    return redirect('gimnasio:ver_alumnos')
                return redirect('gimnasio:lista_pagos')
            except Exception as e:
                messages.error(request, f"Error al registrar el pago: {str(e)}")
        else:
            print("Form errors:", form.errors)  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        initial_data = {}
        if alumno:
            initial_data['alumno'] = alumno.id
        form = PagoCuotaForm(initial=initial_data)
        
        if alumno:
            form.fields['alumno'].widget.attrs['readonly'] = True
            form.fields['alumno'].widget.attrs['disabled'] = True
            form.fields['alumno'].required = False
    
    context = {
        'form': form,
        'alumno': alumno,
        'alumno_id': alumno_id,
        'title': f"Registrar Pago para {alumno.nombre}" if alumno else "Registrar Nuevo Pago"
    }
    
    return render(request, 'gimnasio/pagos/registrar_pago.html', context)

@login_required
def lista_pagos(request):
    if not request.user.perfil.es_profesor:
        messages.error(request, "No tienes permisos para ver los pagos.")
        return redirect('gimnasio:index')
    
    pagos = PagoCuota.objects.all().order_by('-fecha_pago')
    
    alumno_id = request.GET.get('alumno')
    if alumno_id:
        pagos = pagos.filter(alumno_id=alumno_id)
    
    mes = request.GET.get('mes')
    if mes:
        try:
            mes_date = datetime.strptime(mes, '%Y-%m').date()
            pagos = pagos.filter(
                mes_correspondiente__year=mes_date.year,
                mes_correspondiente__month=mes_date.month
            )
        except ValueError:
            messages.warning(request, "Formato de mes inválido.")
    
    alumnos = Alumno.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'pagos': pagos,
        'alumnos': alumnos,
        'current_alumno': alumno_id,
        'current_mes': mes,
    }
    
    return render(request, 'gimnasio/pagos/lista_pagos.html', context)

@login_required
def detalle_pago(request, pago_id):
    if not request.user.perfil.es_profesor:
        messages.error(request, "No tienes permisos para ver los detalles del pago.")
        return redirect('gimnasio:index')
    
    try:
        pago = PagoCuota.objects.get(id=pago_id)
    except PagoCuota.DoesNotExist:
        messages.error(request, "El pago especificado no existe.")
        return redirect('gimnasio:lista_pagos')
    
    context = {
        'pago': pago,
        'title': f"Detalle del Pago - {pago.alumno.nombre}"
    }
    
    return render(request, 'gimnasio/pagos/detalle_pago.html', context)

@login_required
def ver_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    if not es_profesor(request.user) and rutina.alumno.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver esta rutina')
        return redirect('gimnasio:perfil_alumno')
    
    ejercicios = RutinaEjercicio.objects.filter(rutina=rutina).order_by('orden')
    return render(request, 'gimnasio/rutinas/detalle_rutina.html', {
        'rutina': rutina,
        'ejercicios': ejercicios
    })

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
            rutinas = Rutina.objects.filter(alumno=alumno)
            return render(request, 'gimnasio/mis_rutinas.html', {
                'rutinas': rutinas,
                'alumno': alumno
            })
        except Alumno.DoesNotExist:
            messages.warning(request, 'Primero debes completar tu perfil de alumno.')
            return redirect('gimnasio:crear_perfil_alumno')
            
    except Perfil.DoesNotExist:
        Perfil.objects.create(usuario=request.user, es_profesor=False)
        return redirect('gimnasio:crear_perfil_alumno')

@login_required
def detalle_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    
    if not (es_profesor(request.user) or request.user.alumno == rutina.alumno):
        messages.error(request, 'No tienes permiso para ver esta rutina.')
        return redirect('gimnasio:index')
    
    ejercicios = RutinaEjercicio.objects.filter(rutina=rutina).order_by('orden')
    
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

@login_required
@user_passes_test(es_profesor)
def asignar_rutina(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    if request.method == 'POST':
        rutina = Rutina.objects.create(
            alumno=alumno,
            profesor=request.user
        )
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
def gestionar_horario(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if request.method == 'POST':
        dias = request.POST.getlist('dias')
        horario = request.POST.get('horario')
        
        alumno.dias_asistencia.clear()
        for dia_id in dias:
            dia = DiaAsistencia.objects.get(id=dia_id)
            alumno.dias_asistencia.add(dia)
        
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
def crear_rutina_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        ejercicio_forms = []
        
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
            
            for i, ejercicio_data in enumerate(ejercicios_data, start=1):
                ejercicio, _ = Ejercicio.objects.get_or_create(
                    nombre=ejercicio_data['nombre_ejercicio'],
                    grupo_muscular=ejercicio_data['grupo_muscular'],
                    defaults={
                        'descripcion': '',
                        'creado_por': request.user
                    }
                )
                
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
def get_ejercicios_por_grupo(request):
    grupo = request.GET.get('grupo')
    if grupo:
        ejercicios = Ejercicio.objects.filter(grupo_muscular=grupo).values('id', 'nombre')
    else:
        ejercicios = Ejercicio.objects.all().values('id', 'nombre')
    return JsonResponse(list(ejercicios), safe=False)

@login_required
@user_passes_test(es_profesor)
def perfil_profesor(request):
    """Muestra y gestiona el perfil del profesor."""
    try:
        # Obtener el perfil del profesor con relaciones optimizadas
        profesor = request.user.perfil
        
        if request.method == 'POST':
            # Actualizar datos del usuario
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.email = request.POST.get('email')
            request.user.save()
            
            # Actualizar datos del perfil
            profesor.especialidad = request.POST.get('especialidad')
            profesor.biografia = request.POST.get('biografia')
            
            # Manejar la foto de perfil
            if request.FILES.get('foto'):
                profesor.foto = request.FILES['foto']
            
            profesor.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('gimnasio:perfil_profesor')
        
        # Obtener estadísticas
        estadisticas = {
            'total_alumnos': Alumno.objects.filter(profesor=request.user, activo=True).count(),
            'rutinas_activas': Rutina.objects.filter(profesor=request.user, activa=True).count(),
        }
        
        context = {
            'perfil': profesor,
            'total_alumnos': estadisticas['total_alumnos'],
            'rutinas_activas': estadisticas['rutinas_activas'],
            'user': request.user
        }
        
        return render(request, 'gimnasio/perfil_profesor.html', context)
    except Exception as e:
        messages.error(request, f'Error al cargar el perfil: {str(e)}')
        return redirect('gimnasio:index')
