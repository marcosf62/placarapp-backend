
from rest_framework import serializers
from .models import Cliente, Direccion
from .models import Cliente, Direccion, Resena

class DireccionResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ("id", "calle", "numero", "ciudad", "codigo_postal")


class ClienteResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ("id", "nombre", "apellido", "email")


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ("usuario",)
        model = Cliente
        fields = (
            "id",
            "usuario",
            "nombre",
            "apellido",
            "email",
            "telefono",
        )


class ClienteListSerializer(ClienteSerializer):
    direcciones = DireccionResumenSerializer(many=True, read_only=True)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ("direcciones",)


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ("cliente",)
        model = Direccion
        fields = (
            "id",
            "cliente",
            "calle",
            "numero",
            "ciudad",
            "codigo_postal",
        )


class DireccionListSerializer(DireccionSerializer):
    cliente = ClienteResumenSerializer(read_only=True)

    class Meta(DireccionSerializer.Meta):
        fields = (
            "id",
            "cliente",
            "calle",
            "numero",
            "ciudad",
            "codigo_postal",
        )


class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = (
            "id",
            "cliente",
            "producto",
            "puntuacion",
            "comentario",
            "fecha",
        )
        read_only_fields = ("cliente", "fecha")


class ResenaListSerializer(serializers.ModelSerializer):
    cliente = ClienteResumenSerializer(read_only=True)
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True
    )

    class Meta:
        model = Resena
        fields = (
            "id",
            "cliente",
            "producto",
            "producto_nombre",
            "puntuacion",
            "comentario",
            "fecha",
        )
