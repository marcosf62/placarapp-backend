from django.db import models

class Pedido(models.Model):
    ESTADO_CHOICES = [

        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),

    ]


    TIPO_ENTREGA_CHOICES = [

        ('RETIRO', 'Retiro en Sucursal'),
        ('ENVIO', 'Envio a Domicilio'),

    ]


    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, related_name='pedidos')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA_CHOICES)


    #relaciones segun el tipo de entrega elegido
    sucursal_retiro = models.ForeignKey('logistica.Sucursal', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_retiro')
    direccion_envio = models.ForeignKey('clientes.Direccion', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_envio')


    def __str__(self):
        return f"Pedido #{self.id}  Cliente: {self.cliente}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles_pedido')
    producto = models.ForeignKey('catalogo.Producto', on_delete=models.PROTECT, related_name='detalles_pedido')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.cantidad}x Producto ID {self.producto_id} (Pedido #{self.pedido.id})'


class Pago(models.Model):
    METODO_PAGO_CHOICES = [

        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('EFECTIVO', 'Efectivo'),

    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=30, choices=METODO_PAGO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_monto = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    transaccion_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f'Pago #{self.id} Pedido #{self.pedido.id} {"Aprobado" if self.aprobado else "Pendiente"}'
