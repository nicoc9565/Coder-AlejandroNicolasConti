from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'gimnasio'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', LoginView.as_view(template_name='gimnasio/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil de Alumno
    path('perfil/', views.perfil_alumno, name='perfil_alumno'),
    path('perfil/crear/', views.crear_perfil_alumno, name='crear_perfil_alumno'),
    path('perfil/progreso/registrar/', views.registrar_progreso, name='registrar_progreso'),
    
    # Rutinas
    path('rutina/<int:rutina_id>/', views.ver_rutina, name='ver_rutina'),
    path('ejercicio/<int:detalle_rutina_id>/completar/', views.completar_ejercicio, name='completar_ejercicio'),
    
    # Panel de Profesor
    path('panel-profesor/', views.panel_profesor, name='panel_profesor'),
    path('alumno/<int:alumno_id>/rutina/', views.gestionar_rutina, name='gestionar_rutina'),
    path('alumno/<int:alumno_id>/pago/', views.registrar_pago, name='registrar_pago'),
]
