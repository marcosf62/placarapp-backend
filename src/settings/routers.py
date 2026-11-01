from rest_framework.routers import DefaultRouter

from catalogo.views import CategoriaViewSet, MaterialViewSet, ProductoViewSet

router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categorias_vs')
router.register('materiales', MaterialViewSet, basename='materiales_vs')
router.register('productos', ProductoViewSet, basename='productos_vs')