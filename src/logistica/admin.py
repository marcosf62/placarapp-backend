"""Admin de la app logistica: filtros, orden y búsqueda."""
from django.contrib import admin

from .models import Envio, MovimientoStock, Proveedor, Sucursal


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "direccion", "telefono", "activo")
    list_filter = ("activo", "ciudad")
    search_fields = ("nombre", "ciudad", "direccion")
    ordering = ("nombre",)
    list_editable = ("activo",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "activo", "fecha_alta")
    list_filter = ("activo", "fecha_alta")
    search_fields = ("nombre", "email", "telefono")
    ordering = ("nombre",)
    list_editable = ("activo",)


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ("fecha", "producto", "tipo", "cantidad", "proveedor")
    list_filter = ("tipo", "fecha", "proveedor")
    search_fields = ("proveedor__nombre", "observaciones")
    ordering = ("-fecha",)
    date_hierarchy = "fecha"
    readonly_fields = ("fecha",)
    autocomplete_fields = ("proveedor",)


@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pedido",
        "estado",
        "transportista",
        "codigo_seguimiento",
        "fecha_envio",
        "fecha_entrega",
    )
    list_filter = ("estado", "transportista", "fecha_envio")
    search_fields = ("codigo_seguimiento", "transportista", "observaciones")
    ordering = ("-id",)
    date_hierarchy = "fecha_envio"
