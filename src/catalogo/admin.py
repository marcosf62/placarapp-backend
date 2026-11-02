from django.contrib import admin

from .models import Categoria, Material, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "destacado", "activo")
    list_filter = ("categoria", "materiales", "destacado", "activo")
    search_fields = ("nombre", "descripcion", "categoria__nombre", "materiales__nombre")
    ordering = ("nombre",)
    filter_horizontal = ("materiales",)