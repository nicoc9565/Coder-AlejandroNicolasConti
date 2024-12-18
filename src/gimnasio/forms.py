from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Rutina, RutinaEjercicio, EjercicioCompletado, Alumno, Ejercicio

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = 'Tu contraseña debe tener al menos 8 caracteres y no puede ser demasiado común.'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].help_text = 'Ingresa la misma contraseña que antes, para verificación.'

class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ['nombre', 'descripcion', 'alumno']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la rutina'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la rutina'}),
            'alumno': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'nombre': 'Ingresa un nombre descriptivo para la rutina.',
            'descripcion': 'Describe el objetivo y características de la rutina.',
            'alumno': 'Selecciona el alumno para quien es esta rutina.',
        }

class RutinaEjercicioForm(forms.ModelForm):
    grupo_muscular = forms.ChoiceField(
        choices=[
            ('Pecho', 'Pecho'),
            ('Espalda', 'Espalda'),
            ('Piernas', 'Piernas'),
            ('Hombros', 'Hombros'),
            ('Brazos', 'Brazos'),
            ('Abdominales', 'Abdominales'),
            ('Cardio', 'Cardio'),
            ('General', 'General'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    nombre_ejercicio = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Peso Muerto Convencional'
        })
    )
    
    class Meta:
        model = RutinaEjercicio
        fields = ['series', 'repeticiones', 'peso']
        widgets = {
            'series': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'repeticiones': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 8-12 o 15'}),
            'peso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10kg o Peso corporal'}),
        }
        help_texts = {
            'series': 'Número de series a realizar',
            'repeticiones': 'Número o rango de repeticiones por serie',
            'peso': 'Peso a utilizar (en kg) o "Peso corporal"',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar ejercicios por grupo muscular cuando se seleccione
        if 'grupo_muscular' in self.data:
            self.fields['ejercicio'].queryset = Ejercicio.objects.filter(
                grupo_muscular=self.data['grupo_muscular']
            )

class EjercicioCompletadoForm(forms.ModelForm):
    class Meta:
        model = EjercicioCompletado
        fields = ['series_completadas', 'peso_usado', 'notas']
        widgets = {
            'series_completadas': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_usado': forms.NumberInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'edad', 'altura', 'peso', 'dias_asistencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '100'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'min': '100', 'max': '250', 'step': '0.1'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'min': '30', 'max': '300', 'step': '0.1'}),
            'dias_asistencia': forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        }
        help_texts = {
            'altura': 'Altura en centímetros',
            'peso': 'Peso en kilogramos',
            'dias_asistencia': 'Selecciona los días que asistirás al gimnasio',
        }
