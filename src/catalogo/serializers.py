from rest_framework import serializers

from .models import Categoria, Material, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "activa"]
        read_only_fields = ["id"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "nombre", "descripcion"]
        read_only_fields = ["id"]


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "categoria",
            "materiales",
            "destacado",
            "activo",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value


class ProductoListSerializer(ProductoSerializer):
    categoria = CategoriaSerializer(read_only=True)
    materiales = MaterialSerializer(many=True, read_only=True)