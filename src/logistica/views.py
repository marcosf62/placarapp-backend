"""ViewSets de la app logistica.

- ProveedorViewSet        CRUD, nested en list, búsqueda, @action movimientos
- EnvioViewSet            CRUD, nested en list, filtros, @action marcar_entregado
- MovimientoStockViewSet  solo lectura, filtros
- SucursalViewSet         solo lectura (se administra desde el admin)

Requiere `django-filter` (uv add django-filter) y 'django_filters' en
INSTALLED_APPS. La paginación sale de REST_FRAMEWORK en settings.py.
"""
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Envio, MovimientoStock, Proveedor, Sucursal
from .serializers import (
    EnvioListSerializer,
    EnvioSerializer,
    MovimientoStockResumenSerializer,
    MovimientoStockSerializer,
    ProveedorListSerializer,
    ProveedorSerializer,
    SucursalSerializer,
)

# Backends declarados acá para que funcionen aunque settings.py no los defina.
FILTER_BACKENDS = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = FILTER_BACKENDS
    filterset_fields = ["activo"]
    search_fields = ["nombre", "email", "telefono"]
    ordering_fields = ["nombre", "fecha_alta"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.prefetch_related("movimientos")
        return qs

    def get_serializer_class(self):
        # Datos anidados solo cuando se consulta el listado.
        if self.action == "list":
            return ProveedorListSerializer
        return ProveedorSerializer

    @action(detail=True, methods=["get"])
    def movimientos(self, request, pk=None):
        """Movimientos de stock de un proveedor (filtrable con ?tipo=ENTRADA)."""
        proveedor = self.get_object()
        qs = proveedor.movimientos.all()
        tipo = request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo.upper())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MovimientoStockResumenSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(MovimientoStockResumenSerializer(qs, many=True).data)


class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.select_related("pedido")
    permission_classes = [IsAuthenticated]
    filter_backends = FILTER_BACKENDS
    filterset_fields = ["estado", "transportista"]
    search_fields = ["codigo_seguimiento", "transportista", "observaciones"]
    ordering_fields = ["id", "fecha_envio", "fecha_entrega_estimada", "costo_envio"]

    def get_serializer_class(self):
        # Datos anidados (pedido) solo cuando se consulta el listado.
        if self.action == "list":
            return EnvioListSerializer
        return EnvioSerializer

    @action(detail=True, methods=["post"])
    def marcar_entregado(self, request, pk=None):
        """Marca el envío como ENTREGADO y el pedido asociado también."""
        envio = self.get_object()
        if envio.estado == Envio.Estado.ENTREGADO:
            return Response(
                {"detail": "El envío ya fue entregado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if envio.estado == Envio.Estado.CANCELADO:
            return Response(
                {"detail": "No se puede entregar un envío cancelado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            envio.estado = Envio.Estado.ENTREGADO
            envio.fecha_entrega = timezone.localdate()
            envio.save(update_fields=["estado", "fecha_entrega"])
            pedido = envio.pedido
            pedido.estado = "ENTREGADO"
            pedido.save(update_fields=["estado"])
        return Response(EnvioSerializer(envio).data)


class MovimientoStockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoStock.objects.select_related("proveedor")
    serializer_class = MovimientoStockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = FILTER_BACKENDS
    filterset_fields = ["tipo", "producto", "proveedor"]
    search_fields = ["observaciones", "proveedor__nombre"]
    ordering_fields = ["fecha", "cantidad"]


class SucursalViewSet(viewsets.ReadOnlyModelViewSet):
    """Sucursales de retiro: públicas de lectura; se cargan desde el admin."""

    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [AllowAny]
    filter_backends = FILTER_BACKENDS
    filterset_fields = ["ciudad", "activo"]
    search_fields = ["nombre", "ciudad", "direccion"]
    ordering_fields = ["nombre", "ciudad"]
