from django.http import HttpResponse
from django.shortcuts import render


def saludar(request):
    return HttpResponse("Hola desde Django!")


def saludar_con_parametros(request, nombre: str, apellido: str):
    nombre = nombre.capitalize()
    apellido = apellido.capitalize()
    return HttpResponse(f"{apellido}, {nombre}")


def index(request):
    context = {"año": 2024}
    return render(request, "core/index.html", context)


def tirar_dado(request):
    from datetime import datetime
    from random import randint

    tiro_de_dado = randint(1, 6)

    if tiro_de_dado == 6:
        mensaje = f"Has tirado el 🎲 y has sacado ¡{tiro_de_dado}! 😊 ✨ Ganaste ✨"
    else:
        mensaje = f"Has tirado el 🎲 y has sacado ¡{tiro_de_dado}! 😒 Sigue intentando. Presiona F5"

    datos = {
        "title": "Tiro de Dados",
        "mensaje": mensaje,
        "fecha": datetime.now(),
    }
    return render(request, "core/dados.html", context=datos)


def template(request):
    datos = {
        "title": "Ejercicio",
        "name": "Nicolas",
        "apellido": "Conti",
    }
    return render(request, "core/template.html", context=datos)


def ver_notas(request):
    lista_notas = [10, 8, 3, 7, 4, 5, 8]
    return render(request, "core/notas.html", {"notas": lista_notas})


def template2(request):
    usuarios = [
        {"nombre": "juan", "email": "juan@django"},
        {"nombre": "santi", "email": "santi@django"},
        {"nombre": "agustín", "email": "agus@django"},
    ]

    return render(request, "core/template2.html", {"usuarios": usuarios})
