from django.db import models
from django.contrib.auth.models import User

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

    class Meta:
        verbose_name = "Día de Asistencia"
        verbose_name_plural = "Días de Asistencia"

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    es_profesor = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {'Profesor' if self.es_profesor else 'Alumno'}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

class Alumno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)  # Mantenemos el campo nombre para compatibilidad
    edad = models.PositiveIntegerField()
    altura = models.DecimalField(max_digits=5, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dias_asistencia = models.ManyToManyField(DiaAsistencia, blank=True)
    horario = models.CharField(max_length=20, choices=[
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
        ('Noche', 'Noche')
    ], default='Mañana')
    cuota_pagada = models.BooleanField(default=False)

    def __str__(self):
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        return self.nombre

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

class CategoriaEjercicio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de Ejercicio"
        verbose_name_plural = "Categorías de Ejercicios"

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaEjercicio, on_delete=models.CASCADE, related_name='ejercicios')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        unique_together = ['nombre', 'categoria']

class Rutina(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='rutinas')
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutinas_asignadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ejercicios = models.ManyToManyField(Ejercicio, through='DetalleRutina')
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Rutina de {self.alumno} - {self.fecha_creacion.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ['-fecha_creacion']

class DetalleRutina(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='detalles')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField()
    repeticiones = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.series}x{self.repeticiones}"

    class Meta:
        verbose_name = "Detalle de Rutina"
        verbose_name_plural = "Detalles de Rutinas"
        ordering = ['orden']

class EjercicioCompletado(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='ejercicios_completados')
    detalle_rutina = models.ForeignKey(DetalleRutina, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    series_completadas = models.PositiveIntegerField()
    peso_usado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - {self.detalle_rutina.ejercicio} - {self.fecha.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Ejercicio Completado"
        verbose_name_plural = "Ejercicios Completados"
        ordering = ['-fecha']

class RegistroProgreso(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='registros_progreso')
    fecha = models.DateField(auto_now_add=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - Progreso {self.fecha}"

    class Meta:
        verbose_name = "Registro de Progreso"
        verbose_name_plural = "Registros de Progreso"
        ordering = ['-fecha']
        unique_together = ['alumno', 'fecha']

class PagoCuota(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    mes_correspondiente = models.DateField()
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - Pago {self.mes_correspondiente.strftime('%Y-%m')}"

    class Meta:
        verbose_name = "Pago de Cuota"
        verbose_name_plural = "Pagos de Cuotas"
        ordering = ['-fecha_pago']
        unique_together = ['alumno', 'mes_correspondiente']
