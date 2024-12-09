from django.urls import path, include

from .views import index, about

app_name = "gimnasio"

urlpatterns = [
    path("", index, name="index"),
    path("about/", about, name="about"),
]
