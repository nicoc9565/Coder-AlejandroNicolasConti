import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtor_complex.settings')
django.setup()

from django.contrib.auth.models import User
from gimnasio.models import Perfil, Alumno
from django.db import transaction

def reset_and_create_users():
    # Eliminar todos los usuarios existentes
    User.objects.all().delete()
    
    # Crear usuario profesor/administrador
    with transaction.atomic():
        # Crear profesor
        profesor = User.objects.create_user(
            username='profesor',
            email='profesor@mtor-complex.com',
            password='profesor123',
            first_name='Juan',
            last_name='Pérez'
        )
        profesor.is_staff = True
        profesor.is_superuser = True
        profesor.save()
        
        # Crear perfil de profesor
        Perfil.objects.create(
            usuario=profesor,
            es_profesor=True
        )
        
        # Crear alumno
        alumno_user = User.objects.create_user(
            username='alumno',
            email='alumno@example.com',
            password='alumno123',
            first_name='María',
            last_name='González'
        )
        
        # Crear perfil de alumno
        perfil_alumno = Perfil.objects.create(
            usuario=alumno_user,
            es_profesor=False
        )
        
        # Crear registro de alumno
        Alumno.objects.create(
            usuario=alumno_user,
            nombre='María González',
            edad=25,
            altura=1.65,
            peso=65.0,
            horario='Mañana'
        )

    print("Usuarios creados exitosamente:")
    print("Profesor:")
    print("  Username: profesor")
    print("  Password: profesor123")
    print("\nAlumno:")
    print("  Username: alumno")
    print("  Password: alumno123")

if __name__ == '__main__':
    reset_and_create_users()
