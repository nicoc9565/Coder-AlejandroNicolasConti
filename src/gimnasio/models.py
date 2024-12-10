from django.db import models


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    altura = models.DecimalField(max_digits=5, decimal_places=2)
    dias_asistencia = models.CharField(max_length=100)
    horario = models.TimeField()
    cuota_pagada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
