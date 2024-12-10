from django.shortcuts import render, redirect

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Alumno


class AlumnoCreateView(CreateView):
    model = Alumno
    fields = ["nombre", "edad", "altura", "dias_asistencia", "horario", "cuota_pagada"]
    template_name = "gimnasio/alumno_form.html"
    success_url = reverse_lazy("alumno-list")


def nuevo_alumno(request):
    if request.method == "POST":

        nombre = request.POST.get("nombre")

        Alumno.objects.create(nombre=nombre)

        return redirect("/alumnos/")

    return render(request, "gimnasio/alumno_form.html")


def lista_alumnos(request):
    alumnos = Alumno.objects.all()
    return render(request, "gimnasio/alumno_lista.html", {"alumnos": alumnos})


def index(request):
    return render(request, "gimnasio/index.html")


def about(request):
    return render(request, "gimnasio/about.html")
