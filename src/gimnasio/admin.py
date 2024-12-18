from django.contrib import admin
from .models import *

@admin.register(DiaAsistencia)
class DiaAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('dia',)
    search_fields = ('dia',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'es_profesor', 'fecha_registro')
    list_filter = ('es_profesor',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'profesor', 'activo']
    list_filter = ['activo', 'profesor']
    search_fields = ['nombre', 'usuario__username']
    filter_horizontal = ('dias_asistencia',)

@admin.register(CategoriaEjercicio)
class CategoriaEjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'grupo_muscular', 'creado_por', 'fecha_creacion')
    list_filter = ('grupo_muscular', 'creado_por')
    search_fields = ('nombre', 'descripcion')

class RutinaEjercicioInline(admin.TabularInline):
    model = RutinaEjercicio
    extra = 1

@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'profesor', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('profesor', 'fecha_creacion')
    search_fields = ('alumno__nombre', 'profesor__username')
    inlines = [RutinaEjercicioInline]
    date_hierarchy = 'fecha_creacion'
