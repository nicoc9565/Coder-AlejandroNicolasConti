from django.urls import path
from . import views

app_name = 'gimnasio'

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    
    # URLs para alumnos
    path('perfil/alumno/', views.perfil_alumno, name='perfil_alumno'),
    path('perfil/alumno/crear/', views.crear_perfil_alumno, name='crear_perfil_alumno'),
    path('mis-rutinas/', views.ver_mis_rutinas, name='mis_rutinas'),
    path('rutina/<int:rutina_id>/', views.detalle_rutina, name='detalle_rutina'),
    path('ejercicio/<int:detalle_rutina_id>/completar/', views.registrar_ejercicio_completado, name='completar_ejercicio'),
    path('progreso/registrar/', views.registrar_progreso, name='registrar_progreso'),
    
    # URLs para profesores
    path('profesor/panel/', views.panel_profesor, name='panel_profesor'),
    path('profesor/perfil/', views.perfil_profesor, name='perfil_profesor'),
    path('profesor/alumnos/', views.ver_alumnos, name='ver_alumnos'),
    path('profesor/rutina/crear/', views.crear_rutina, name='crear_rutina'),
    path('profesor/alumno/<int:alumno_id>/rutina/nueva/', views.crear_rutina_alumno, name='crear_rutina_alumno'),
    path('profesor/rutina/<int:rutina_id>/ejercicios/', views.agregar_ejercicios_rutina, name='agregar_ejercicios_rutina'),
    path('profesor/rutina/<int:rutina_id>/activar/', views.activar_rutina, name='activar_rutina'),
    path('profesor/rutina/<int:rutina_id>/desactivar/', views.desactivar_rutina, name='desactivar_rutina'),
    path('profesor/alumno/<int:alumno_id>/rutina/', views.gestionar_rutina, name='gestionar_rutina'),
    path('profesor/alumno/<int:alumno_id>/pago/', views.registrar_pago, name='registrar_pago'),
    path('profesor/alumno/<int:alumno_id>/progreso/', views.ver_progreso, name='ver_progreso'),
    path('profesor/alumno/<int:alumno_id>/horario/', views.gestionar_horario, name='gestionar_horario'),
    path('ejercicios/', views.gestionar_ejercicios, name='gestionar_ejercicios'),
    path('ejercicios/editar/<int:ejercicio_id>/', views.editar_ejercicio, name='editar_ejercicio'),
    path('ejercicios/eliminar/<int:ejercicio_id>/', views.eliminar_ejercicio, name='eliminar_ejercicio'),
    path('api/ejercicios/', views.get_ejercicios_por_grupo, name='get_ejercicios_por_grupo'),
]
