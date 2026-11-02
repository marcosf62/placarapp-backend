
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .routers import router


urlpatterns = [
    path("admin/", admin.site.urls),

    # Rutas generales de la API
    path("api/", include(router.urls)),

    # Aplicaciones
    path("api/ventas/", include("ventas.urls")),
    path("api/logistica/", include("logistica.urls")),
    path("api/clientes/", include("clientes.urls")),

    # Autenticación
    path("api/token/", obtain_auth_token, name="api_token_auth"),
    path("api-auth/", include("rest_framework.urls")),

    # Documentación
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
