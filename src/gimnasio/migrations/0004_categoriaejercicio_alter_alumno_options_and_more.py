# Generated by Django 5.0 on 2024-12-18 12:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gimnasio', '0003_auto_20241218_0946'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaEjercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('descripcion', models.TextField()),
            ],
            options={
                'verbose_name': 'Categoría de Ejercicio',
                'verbose_name_plural': 'Categorías de Ejercicios',
            },
        ),
        migrations.AlterModelOptions(
            name='alumno',
            options={'verbose_name': 'Alumno', 'verbose_name_plural': 'Alumnos'},
        ),
        migrations.AlterModelOptions(
            name='diaasistencia',
            options={'verbose_name': 'Día de Asistencia', 'verbose_name_plural': 'Días de Asistencia'},
        ),
        migrations.AddField(
            model_name='alumno',
            name='peso',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='alumno',
            name='usuario',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='alumno',
            name='dias_asistencia',
            field=models.ManyToManyField(blank=True, to='gimnasio.diaasistencia'),
        ),
        migrations.AlterField(
            model_name='diaasistencia',
            name='dia',
            field=models.CharField(choices=[('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'), ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], max_length=20),
        ),
        migrations.CreateModel(
            name='Ejercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='ejercicios/')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ejercicios', to='gimnasio.categoriaejercicio')),
            ],
            options={
                'verbose_name': 'Ejercicio',
                'verbose_name_plural': 'Ejercicios',
                'unique_together': {('nombre', 'categoria')},
            },
        ),
        migrations.CreateModel(
            name='DetalleRutina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.PositiveIntegerField()),
                ('repeticiones', models.PositiveIntegerField()),
                ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('notas', models.TextField(blank=True)),
                ('ejercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gimnasio.ejercicio')),
            ],
            options={
                'verbose_name': 'Detalle de Rutina',
                'verbose_name_plural': 'Detalles de Rutinas',
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_profesor', models.BooleanField(default=False)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil',
                'verbose_name_plural': 'Perfiles',
            },
        ),
        migrations.CreateModel(
            name='Rutina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutinas', to='gimnasio.alumno')),
                ('ejercicios', models.ManyToManyField(through='gimnasio.DetalleRutina', to='gimnasio.ejercicio')),
                ('profesor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutinas_asignadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Rutina',
                'verbose_name_plural': 'Rutinas',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.AddField(
            model_name='detallerutina',
            name='rutina',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='gimnasio.rutina'),
        ),
        migrations.AlterUniqueTogether(
            name='detallerutina',
            unique_together={('rutina', 'ejercicio')},
        ),
    ]
