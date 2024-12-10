from django.db import models


class DiaAsistencia(models.Model):
    dia = models.CharField(
        max_length=20,
        choices=[
            ("Lunes", "Lunes"),
            ("Martes", "Martes"),
            ("Miércoles", "Miércoles"),
            ("Jueves", "Jueves"),
            ("Viernes", "Viernes"),
            ("Sábado", "Sábado"),
            ("Domingo", "Domingo"),
        ],
    )

    def __str__(self):
        return self.dia


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    altura = models.DecimalField(max_digits=5, decimal_places=2)
    dias_asistencia = models.ManyToManyField(DiaAsistencia)
    horario = models.TimeField()
    cuota_pagada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
