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

## Tecnologías Utilizadas

- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Backend:** Python, Django
- **Bases de datos:** SQLite
- **Gestión de dependencias:** Virtualenv
- **Otras herramientas:** Bootstrap Icons, Milligram, Normalize.css

---

## Características Principales

- **Gestión de alumnos:** Registro y visualización de datos de los alumnos inscritos.
- **Dashboard:** Panel de control para el dueño del gimnasio con reportes detallados.
- **Responsive Design:** Optimizado para dispositivos móviles, tabletas y computadoras.
- **Estilo Moderno:** Uso de Bootstrap y estilos personalizados.
- **Gestión de rutinas:** Registro y visualización de rutinas y ejercicios.
- **Gestión de asistencias:** Registro y visualización de asistencias de los alumnos.
- **Gestión de pagos:** Registro y visualización de pagos de los alumnos.
## Todo esto es lo que me gustaria lograr con este proyecto

---

## Configuración y Pruebas

Sigue estos pasos para probar el proyecto en tu entorno local:

1. Clona este repositorio:
   git clone https://github.com/nicoc9565/MTOR-COMPLEX.git

2. Accede al directorio del proyecto:
   cd MTOR-COMPLEX

3. Crea y activa un entorno virtual:
   python -m venv .venv
   source .venv/bin/activate   # En Windows usa .venv\Scripts\activate

4. Instala las dependencias:
    uv sync

5. Realiza las migraciones y ejecuta el servidor:
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver

6. Abre tu navegador y accede a `http://127.0.0.1:8000/`.

---

## Estructura del Proyecto

```
MTOR-COMPLEX/
├── gimnasio/               # Aplicación principal
├── static/                 # Archivos estáticos (CSS, imágenes, JS)
├── templates/              # Plantillas HTML
├── .venv/                  # Entorno virtual
├── manage.py               # Archivo principal de Django
└── README.md               # Este archivo
```

---

## Contribuciones

Si tienes sugerencias o mejoras para este proyecto, no dudes en hacer un fork del repositorio y enviar un pull request. También puedes abrir un *issue* con tus ideas o problemas.

---

**© 2024 MTOR-COMPLEX** - Todos los derechos reservados.
