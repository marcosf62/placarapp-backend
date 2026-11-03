"""Rutas de la app logistica (mismo patrón que ventas).

En settings/urls.py se incluye con:
    path('api/logistica/', include('logistica.urls')),
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EnvioViewSet,
    MovimientoStockViewSet,
    ProveedorViewSet,
    SucursalViewSet,
)

router = DefaultRouter()
router.register(r"proveedores", ProveedorViewSet, basename="proveedor")
router.register(r"movimientos-stock", MovimientoStockViewSet, basename="movimientostock")
router.register(r"envios", EnvioViewSet, basename="envio")
router.register(r"sucursales", SucursalViewSet, basename="sucursal")

urlpatterns = [
    path("", include(router.urls)),
]
