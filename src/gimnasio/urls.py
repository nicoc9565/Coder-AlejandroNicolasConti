from django.urls import path
from . import views

app_name = 'gimnasio'

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar-sesion/', views.cerrar_sesion, name='logout'),
    path('alumno/perfil/', views.perfil_alumno, name='perfil_alumno'),
    path('alumno/rutinas/', views.ver_mis_rutinas, name='mis_rutinas'),
    path('alumno/rutinas/<int:rutina_id>/', views.detalle_rutina, name='detalle_rutina'),
    path('alumno/rutinas/<int:rutina_id>/ejercicios/', views.ejercicios_rutina, name='ejercicios_rutina'),
    path('alumno/progreso/', views.ver_progreso, name='ver_progreso'),
    path('progreso/registrar/', views.registrar_progreso, name='registrar_progreso'),
    path('profesor/panel/', views.panel_profesor, name='panel_profesor'),
    path('profesor/perfil/', views.perfil_profesor, name='perfil_profesor'),
    path('profesor/alumnos/', views.alumnos_profesor, name='alumnos_profesor'),
    path('profesor/ejercicios/', views.gestionar_ejercicios, name='gestionar_ejercicios'),
    path('profesor/rutina/crear/', views.crear_rutina, name='crear_rutina'),
    path('profesor/alumno/<int:alumno_id>/rutina/nueva/', views.crear_rutina_alumno, name='crear_rutina_alumno'),
    path('profesor/alumno/<int:alumno_id>/rutinas/', views.gestionar_rutinas_alumno, name='gestionar_rutinas_alumno'),
    path('profesor/rutina/<int:rutina_id>/editar/', views.editar_rutina, name='editar_rutina'),
    path('profesor/rutina/<int:rutina_id>/eliminar/', views.eliminar_rutina, name='eliminar_rutina'),
    path('profesor/rutina/<int:rutina_id>/activar/', views.activar_rutina, name='activar_rutina'),
    path('profesor/rutina/<int:rutina_id>/desactivar/', views.desactivar_rutina, name='desactivar_rutina'),
    path('profesor/rutina/<int:rutina_id>/ejercicios/', views.ejercicios_rutina_profesor, name='ejercicios_rutina_profesor'),
    path('profesor/ejercicio/crear/', views.crear_ejercicio, name='crear_ejercicio'),
    path('profesor/ejercicio/<int:ejercicio_id>/editar/', views.editar_ejercicio, name='editar_ejercicio'),
    path('profesor/ejercicio/<int:ejercicio_id>/eliminar/', views.eliminar_ejercicio, name='eliminar_ejercicio'),
    path('alumno/rutina/ejercicio/<int:rutina_ejercicio_id>/completar/', views.completar_ejercicio, name='completar_ejercicio'),
]
