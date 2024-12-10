from django.urls import path

from .views import index, about, AlumnoCreateView

from . import views

app_name = "gimnasio"

urlpatterns = [
    path("index", index, name="index"),
    path("about/", about, name="about"),
    path("alumnos/nuevo/", AlumnoCreateView.as_view(), name="alumno-create"),
    path("alumnos/", views.lista_alumnos, name="alumno-list"),
]
