from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DiaAsistencia(models.Model):
    DIAS_CHOICES = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    
    dia = models.CharField(max_length=3, choices=DIAS_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_dia_display()

    class Meta:
        verbose_name = "Día de Asistencia"
        verbose_name_plural = "Días de Asistencia"

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    es_profesor = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    biografia = models.TextField(blank=True)
    especialidad = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {'Profesor' if self.es_profesor else 'Alumno'}"

    def get_foto_url(self):
        if self.foto:
            return self.foto.url
        return '/static/gimnasio/images/default-profile.png'

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

class Alumno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    altura = models.FloatField(help_text='Altura en centímetros')
    peso = models.FloatField(help_text='Peso en kilogramos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    profesor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alumnos_asignados'
    )
    dias_asistencia = models.ManyToManyField(DiaAsistencia, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"

    @property
    def cuota_al_dia(self):
        from datetime import datetime
        mes_actual = datetime.now().date().replace(day=1)
        ultimo_pago = self.pagos.order_by('-mes_correspondiente').first()
        return ultimo_pago and ultimo_pago.mes_correspondiente >= mes_actual

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['nombre']

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
    grupo_muscular = models.CharField(max_length=50, default='General')
    imagen_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['nombre']

class Rutina(models.Model):
    nombre = models.CharField(max_length=100, default='Nueva Rutina')
    descripcion = models.TextField(blank=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='rutinas')
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutinas_asignadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ejercicios = models.ManyToManyField(Ejercicio, through='RutinaEjercicio')
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.alumno}"

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ['-fecha_creacion']

class RutinaEjercicio(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.IntegerField()
    repeticiones = models.CharField(max_length=50)  # Permite rangos como "8-12"
    peso = models.CharField(max_length=50, blank=True)  # Permite rangos o "Peso corporal"
    descanso = models.CharField(max_length=50)  # Ejemplo: "60 segundos"
    orden = models.IntegerField()
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ejercicio de Rutina"
        verbose_name_plural = "Ejercicios de Rutina"
        ordering = ['orden']

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.series}x{self.repeticiones}"

class EjercicioCompletado(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='ejercicios_completados')
    rutina_ejercicio = models.ForeignKey(RutinaEjercicio, on_delete=models.CASCADE, null=True)
    fecha = models.DateTimeField(default=timezone.now)
    series_completadas = models.PositiveIntegerField()
    peso_usado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - {self.rutina_ejercicio} - {self.fecha}"

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
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - Pago {self.mes_correspondiente.strftime('%Y-%m')}"

    class Meta:
        verbose_name = "Pago de Cuota"
        verbose_name_plural = "Pagos de Cuotas"
        ordering = ['-fecha_pago']
        unique_together = ['alumno', 'mes_correspondiente']
