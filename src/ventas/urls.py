from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, DetallePedidoViewSet, PagoViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'detalles', DetallePedidoViewSet, basename='detallepedido')
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    path('', include(router.urls)),
]