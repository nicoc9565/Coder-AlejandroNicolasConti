# Generated by Django 5.0 on 2024-12-18 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gimnasio', '0002_rutina_descripcion_rutina_nombre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagocuota',
            name='comprobante',
        ),
    ]