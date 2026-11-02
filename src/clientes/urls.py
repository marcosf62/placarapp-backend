
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, DireccionViewSet, ResenaViewSet

router = DefaultRouter()

router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"direcciones", DireccionViewSet, basename="direccion")
router.register(r"resenas", ResenaViewSet, basename="resena")

urlpatterns = [
    path("", include(router.urls)),
]
