from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Alumno, DiaAsistencia


class AlumnoCreateView(CreateView):
    model = Alumno
    fields = ["nombre", "edad", "altura", "horario", "cuota_pagada"]
    template_name = "gimnasio/alumno_form.html"
    success_url = reverse_lazy("gimnasio:alumno-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dias"] = DiaAsistencia.objects.all()
        return context

    def form_valid(self, form):
        alumno = form.save()

        dias_asistencia = self.request.POST.getlist("dias_asistencia")
        for dia_id in dias_asistencia:
            dia_obj = DiaAsistencia.objects.get(id=dia_id)
            alumno.dias_asistencia.add(dia_obj)

        alumno.save()

        return super().form_valid(form)


def lista_alumnos(request):
    alumnos = Alumno.objects.all()
    return render(request, "gimnasio/alumno_lista.html", {"alumnos": alumnos})


def index(request):
    return render(request, "gimnasio/index.html")


def about(request):
    return render(request, "gimnasio/about.html")
