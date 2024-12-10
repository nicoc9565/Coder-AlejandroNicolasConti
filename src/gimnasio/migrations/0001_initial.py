# Generated by Django 5.1.3 on 2024-12-10 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('edad', models.PositiveIntegerField()),
                ('altura', models.DecimalField(decimal_places=2, max_digits=5)),
                ('dias_asistencia', models.CharField(max_length=100)),
                ('horario', models.TimeField()),
                ('cuota_pagada', models.BooleanField(default=False)),
            ],
        ),
    ]