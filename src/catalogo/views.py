from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Categoria, Material, Producto
from .serializers import (
    CategoriaSerializer,
    MaterialSerializer,
    ProductoListSerializer,
    ProductoSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    """CRUD de categorías de muebles."""

    queryset = Categoria.objects.all().order_by("id")
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Productos de una categoría",
        description="Lista los productos activos de la categoría indicada.",
        responses=ProductoSerializer(many=True),
    )
    @action(detail=True, methods=["get"])
    def productos(self, request, pk=None):
        categoria = self.get_object()
        queryset = categoria.productos.filter(activo=True).order_by("id")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductoSerializer(queryset, many=True)
        return Response(serializer.data)


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """Materiales disponibles (solo lectura)."""

    queryset = Material.objects.all().order_by("id")
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductoViewSet(viewsets.ModelViewSet):
    """CRUD de productos. El list muestra categoría y materiales anidados."""

    queryset = (
        Producto.objects.all()
        .select_related("categoria")
        .prefetch_related("materiales")
        .order_by("id")
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "categoria": ["exact"],
        "materiales": ["exact"],
        "precio": ["exact", "gt", "lt", "gte", "lte"],
        "destacado": ["exact"],
        "activo": ["exact"],
    }
    search_fields = ["nombre", "descripcion", "categoria__nombre", "materiales__nombre"]
    ordering_fields = ["precio", "id", "nombre", "timestamp"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoListSerializer
        return ProductoSerializer

    @extend_schema(
        summary="Productos destacados",
        description="Lista los productos activos marcados como destacados.",
        responses=ProductoListSerializer(many=True),
    )
    @action(detail=False, methods=["get"])
    def destacados(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(destacado=True, activo=True)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductoListSerializer(queryset, many=True)
        return Response(serializer.data)