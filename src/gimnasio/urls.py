from django.urls import path

from .views import (
    index,
    AlumnoCreateView,
    AlumnoDetailView,
    AlumnoUpdateView,
    AlumnoDeleteView,
)

from . import views

app_name = "gimnasio"

urlpatterns = [
    path("index/", index, name="index"),
    path("alumnos/nuevo/", AlumnoCreateView.as_view(), name="alumno-create"),
    path("alumnos/", views.lista_alumnos, name="alumno-list"),
    path("alumnos/<int:pk>/", AlumnoDetailView.as_view(), name="alumno-detail"),
    path("alumnos/<int:pk>/editar/", AlumnoUpdateView.as_view(), name="alumno-edit"),
    path(
        "alumnos/<int:pk>/eliminar/", AlumnoDeleteView.as_view(), name="alumno-delete"
    ),
]
