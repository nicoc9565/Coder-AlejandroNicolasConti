import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

try:
    superuser = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('Superusuario creado exitosamente')
except IntegrityError:
    print('El superusuario ya existe')
