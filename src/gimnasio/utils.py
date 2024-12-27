from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def es_profesor(user):
    """Verifica si un usuario es profesor."""
    if not user.is_authenticated:
        return False
    try:
        return user.perfil.es_profesor
    except:
        return False

def handle_view_exception(view_func):
    """Decorador para manejar excepciones de manera consistente en las vistas."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('index')
        except Exception as e:
            messages.error(request, "Ha ocurrido un error inesperado")
            return redirect('index')
    return wrapped

def verificar_profesor_alumno(profesor, alumno_id):
    """Verifica si un profesor tiene permiso para gestionar un alumno."""
    from .models import Alumno
    alumno = Alumno.objects.select_related('usuario', 'profesor').get(id=alumno_id)
    if alumno.profesor_id != profesor.id:
        raise PermissionDenied("No tienes permiso para gestionar este alumno")
    return alumno
