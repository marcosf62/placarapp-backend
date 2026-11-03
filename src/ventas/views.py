from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated  # 1. Importar la clase de permisos
from .models import Pedido, DetallePedido, Pago
from .serializers import PedidoSerializer, DetallePedidoSerializer, PagoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-fecha_venta')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]  # 2. Proteger vista
    
    # Agregamos soporte para filtros, búsquedas y ordenamiento
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['estado', 'tipo_entrega', 'cliente__nombre'] # Campos por los que se puede buscar
    ordering_fields = ['fecha_venta', 'monto_total']              # Campos por los que se puede ordenar


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]  # 2. Proteger vista


class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]  # 2. Proteger vista