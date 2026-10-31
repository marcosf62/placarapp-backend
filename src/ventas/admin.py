from django.contrib import admin
from .models import Pedido, DetallePedido, Pago

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'estado', 'total')
    list_filter = ('estado', 'fecha_venta')  # Cumple con "filtros desde el panel"
    search_fields = ('id', 'estado')         # Cumple con "búsqueda desde el panel"
    ordering = ('-fecha_venta',)             # Cumple con "ordenamiento"

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('pedido',)
    search_fields = ('pedido__id', 'producto')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'monto', 'fecha_pago', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
    search_fields = ('id', 'pedido__id', 'metodo_pago')
    ordering = ('-fecha_pago',)