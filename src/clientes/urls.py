
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, DireccionViewSet, ResenaViewSet
from .registration import RegistroClienteView

router = DefaultRouter()

router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"direcciones", DireccionViewSet, basename="direccion")
router.register(r"resenas", ResenaViewSet, basename="resena")

urlpatterns = [
    path("registro/", RegistroClienteView.as_view(), name="registro-cliente"),
    path("", include(router.urls)),
]
