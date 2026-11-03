
from django.contrib import admin
from .models import Cliente, Direccion


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "email", "telefono")
    search_fields = ("nombre", "apellido", "email")
    ordering = ("apellido", "nombre")


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "calle", "numero", "ciudad")
    search_fields = (
        "cliente__nombre",
        "cliente__apellido",
        "calle",
        "ciudad",
    )
    list_filter = ("ciudad",)
    ordering = ("ciudad", "calle")
