from django.shortcuts import render
from rest_framework import viewsets
from .models import Pedido, DetallePedido, Pago
from .serializers import PedidoSerializer, DetallePedidoSerializer, PagoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-fecha_venta')
    serializer_class = PedidoSerializer


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer


class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer