# Generated by Django 5.0 on 2024-12-18 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gimnasio', '0004_categoriaejercicio_alter_alumno_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ejercicio',
            name='imagen',
        ),
    ]