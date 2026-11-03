"""Serializers de la app logistica.

NestedSerializers (solo en `list`, ver get_serializer_class en views.py):
  - ProveedorListSerializer -> anida los movimientos de stock.
  - EnvioListSerializer     -> anida un resumen del pedido.
"""
from rest_framework import serializers

from .models import Envio, MovimientoStock, Proveedor, Sucursal


# ---------------------------------------------------------------------------
# Sucursal
# ---------------------------------------------------------------------------
class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = [
            "id",
            "nombre",
            "direccion",
            "ciudad",
            "telefono",
            "horario_atencion",
            "activo",
        ]


# ---------------------------------------------------------------------------
# MovimientoStock
# ---------------------------------------------------------------------------
class MovimientoStockSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.StringRelatedField(
        source="proveedor", read_only=True
    )

    class Meta:
        model = MovimientoStock
        fields = [
            "id",
            "producto",
            "proveedor",
            "proveedor_nombre",
            "tipo",
            "cantidad",
            "fecha",
            "observaciones",
        ]


class MovimientoStockResumenSerializer(serializers.ModelSerializer):
    """Versión liviana para anidar dentro de otro serializer."""

    class Meta:
        model = MovimientoStock
        fields = ["id", "producto", "tipo", "cantidad", "fecha"]


# ---------------------------------------------------------------------------
# Proveedor
# ---------------------------------------------------------------------------
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            "id",
            "nombre",
            "telefono",
            "email",
            "direccion",
            "activo",
            "fecha_alta",
        ]
        read_only_fields = ["fecha_alta"]


class ProveedorListSerializer(ProveedorSerializer):
    """Usado solo en `list`: incluye los movimientos de stock anidados."""

    movimientos = MovimientoStockResumenSerializer(many=True, read_only=True)

    class Meta(ProveedorSerializer.Meta):
        fields = ProveedorSerializer.Meta.fields + ["movimientos"]


# ---------------------------------------------------------------------------
# Envio
# ---------------------------------------------------------------------------
class PedidoResumenSerializer(serializers.Serializer):
    """Resumen del pedido (app ventas) para anidar en el listado de envíos."""

    id = serializers.IntegerField(read_only=True)
    estado = serializers.CharField(read_only=True)
    tipo_entrega = serializers.CharField(read_only=True)
    monto_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    fecha_venta = serializers.DateTimeField(read_only=True)


class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = [
            "id",
            "pedido",
            "estado",
            "transportista",
            "codigo_seguimiento",
            "costo_envio",
            "fecha_envio",
            "fecha_entrega_estimada",
            "fecha_entrega",
            "observaciones",
        ]

    def validate_pedido(self, pedido):
        if pedido.tipo_entrega != "ENVIO":
            raise serializers.ValidationError(
                "Solo los pedidos con entrega a domicilio (ENVIO) tienen envío."
            )
        return pedido

    def validate(self, attrs):
        # En un PATCH parcial se toman los valores que ya tiene la instancia.
        envio = attrs.get("fecha_envio", getattr(self.instance, "fecha_envio", None))
        entrega = attrs.get(
            "fecha_entrega", getattr(self.instance, "fecha_entrega", None)
        )
        if envio and entrega and entrega < envio:
            raise serializers.ValidationError(
                {"fecha_entrega": "No puede ser anterior a la fecha de envío."}
            )
        return attrs


class EnvioListSerializer(EnvioSerializer):
    """Usado solo en `list`: incluye el resumen del pedido anidado."""

    pedido = PedidoResumenSerializer(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta(EnvioSerializer.Meta):
        fields = EnvioSerializer.Meta.fields + ["estado_display"]
