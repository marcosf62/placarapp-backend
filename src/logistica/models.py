"""Modelos de la app logistica (responsable: Marcos F).

Proveedor, MovimientoStock, Envio y Sucursal.

Sucursal NO figura en el contrato del README, pero ventas.Pedido ya la usa
(`sucursal_retiro = FK('logistica.Sucursal')`), así que tiene que existir acá.
"""
from django.db import models


class Sucursal(models.Model):
    """Local donde el cliente puede retirar su pedido (tipo_entrega = RETIRO)."""

    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)
    horario_atencion = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"


class Proveedor(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class MovimientoStock(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        AJUSTE = "AJUSTE", "Ajuste"

    producto = models.ForeignKey(
        "catalogo.Producto",
        on_delete=models.PROTECT,
        related_name="movimientos_stock",
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos",
        help_text="Solo para entradas de mercadería.",
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "movimiento de stock"
        verbose_name_plural = "movimientos de stock"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} (producto {self.producto_id})"


class Envio(models.Model):
    """Envío a domicilio de un pedido (solo pedidos con tipo_entrega = ENVIO)."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PREPARANDO = "PREPARANDO", "Preparando"
        EN_CAMINO = "EN_CAMINO", "En camino"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    pedido = models.OneToOneField(
        "ventas.Pedido",
        on_delete=models.PROTECT,
        related_name="envio",
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.PENDIENTE
    )
    transportista = models.CharField(max_length=100, blank=True)
    codigo_seguimiento = models.CharField(max_length=50, blank=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_envio = models.DateField(null=True, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "envío"
        verbose_name_plural = "envíos"
        ordering = ["-id"]

    def __str__(self):
        return f"Envío #{self.pk} - {self.get_estado_display()}"
