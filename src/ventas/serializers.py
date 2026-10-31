from rest_framework import serializers
from .models import Pedido, DetallePedido, Pago

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta: 
        model = DetallePedido
        fields = ['id', 'pedido', 'producto', 'cantidad', 'precio_unitario']


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'pedido', 'metodo', 'monto', 'fecha_monto', 'aprobado', 'transaccion_id']

    
class PedidoSerializer(serializers.ModelSerializer):

    #incluimos los serializers anidados para que al consultar un pedido tambien se devuelvan sus items (detalles) y su informacion de pago asociada
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)


    class Meta:
        model = Pedido
        fields = [

            'id',
            'cliente',
            'fecha_venta',
            'monto_total',
            'estado',
            'tipo_entrega',
            'sucursal_retiro',
            'direccion_envio',
            'detalles',
            'pago'


        ]