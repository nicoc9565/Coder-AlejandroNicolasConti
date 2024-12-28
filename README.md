# Curso de Python

## Comisión
Comisión: 60095
Profesor: Esteban Acevedo

## Alumno
Nombre: **Alejandro Nicolas Conti**
Linkedin: https://linkedin.com/in/nicoc95
GitHub: https://github.com/nicoc9565

## Para activar entorno virtual .\.venv\Scripts\Activate.ps1

# MTOR-COMPLEX

**MTOR-COMPLEX** es un proyecto para la gestión integral de un gimnasio. Este sistema permite registrar alumnos, administrar rutinas, gestionar asistencias, controlar pagos y proporcionar un panel de administración para el dueño del gimnasio.

---

**💪 Aplicación de Gestión de Gimnasio

Esta aplicación web está diseñada para gestionar un gimnasio, permitiendo la administración de alumnos, profesores, rutinas y seguimiento de progreso.

## 🌟 Características Principales

### Para Alumnos
- 👤 Perfil personalizado con datos básicos
- 📊 Seguimiento de progreso (peso, asistencias)
- 💪 Visualización de rutinas asignadas
- ✅ Registro de ejercicios completados
- 💰 Control de pagos de cuota

### Para Profesores
- 👥 Gestión de alumnos asignados
- 📝 Creación y asignación de rutinas
- 🎯 Seguimiento del progreso de alumnos
- 📋 Gestión de ejercicios y rutinas

## 🔑 Usuarios de Prueba

### Profesor
- **Usuario:** ivan
- **Contraseña:** admin123
- **Características:**
  - Puede crear y asignar rutinas
  - Gestionar alumnos
  - Ver progreso de alumnos

### Alumno
- **Usuario:** nico
- **Contraseña:** prueba123
- **Características:**
  - Acceso a rutinas personalizadas
  - Registro de progreso
  - Ver historial de ejercicios

## 🚀 Tecnologías Utilizadas

- Django 4.2
- Bootstrap 5
- Chart.js para gráficos
- SQLite como base de datos

## 📱 Funcionalidades Destacadas

1. **Sistema de Autenticación**
   - Registro de usuarios
   - Login personalizado
   - Perfiles diferenciados (alumno/profesor)

2. **Gestión de Rutinas**
   - Creación de rutinas personalizadas
   - Asignación a alumnos
   - Seguimiento de progreso

3. **Seguimiento de Progreso**
   - Gráficos de evolución de peso
   - Registro de asistencias
   - Historial de ejercicios completados

4. **Sistema de Pagos**
   - Control de cuotas mensuales
   - Estado de pagos
   - Historial de transacciones

## 💻 Instalación y Configuración

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/nicoc9565/MTOR-COMPLEX.git
   cd MTOR-COMPLEX
   ```

2. **Configurar Entorno Virtual**
   ```bash
   # Crear entorno virtual
   python -m venv .venv

   # Activar entorno virtual (Windows PowerShell)
   .\.venv\Scripts\Activate.ps1
   # O para Windows CMD
   # .\.venv\Scripts\activate.bat
   ```

3. **Instalar uv y Dependencias**
   ```bash
   # Instalar uv
   python -m pip install uv

   # Instalar dependencias usando uv
   uv pip install --requirement requirements.txt
   # O simplemente
   uv sync
   ```

4. **Configurar la Base de Datos**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Iniciar el Servidor de Desarrollo**
   ```bash
   python manage.py runserver
   ```

6. **Acceder a la Aplicación**
   - Abrir el navegador y visitar: `http://127.0.0.1:8000/`
   - Usar las credenciales proporcionadas en la sección "Usuarios de Prueba"

### 🔍 Notas de Instalación
- Asegúrate de tener Python 3.8 o superior instalado
- uv es más rápido que pip para la instalación de dependencias
- Si encuentras problemas con uv, puedes usar pip como alternativa

---
Desarrollado por Alejandro Nicolás Conti © 2024
