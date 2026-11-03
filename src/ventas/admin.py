from django.contrib import admin
from .models import Pedido, DetallePedido, Pago

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_venta', 'estado', 'monto_total', 'tipo_entrega')
    list_filter = ('estado', 'tipo_entrega', 'fecha_venta')  # Filtros en el panel
    search_fields = ('id', 'estado', 'cliente__id')           # Búsqueda en el panel
    ordering = ('-fecha_venta',)                             # Ordenamiento

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('pedido',)
    search_fields = ('pedido__id', 'producto__id')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'monto', 'fecha_monto', 'metodo', 'aprobado')
    list_filter = ('metodo', 'aprobado', 'fecha_monto')
    search_fields = ('id', 'pedido__id', 'metodo', 'transaccion_id')
    ordering = ('-fecha_monto',)