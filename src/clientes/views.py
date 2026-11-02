
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cliente, Direccion, Resena

from .serializers import (
    ClienteSerializer,
    ClienteListSerializer,
    DireccionSerializer,
    DireccionListSerializer,
    DireccionResumenSerializer,
    ResenaSerializer,
    ResenaListSerializer,
)

from .permissions import IsOwnerOrReadOnly

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["nombre", "apellido"]
    search_fields = ["nombre", "apellido", "email"]
    ordering_fields = ["nombre", "apellido", "id"]
    ordering = ["apellido", "nombre"]

    def get_queryset(self):
        return Cliente.objects.filter(
            usuario=self.request.user
        ).select_related("usuario").prefetch_related("direcciones")

    def get_serializer_class(self):
        if self.action == "list":
            return ClienteListSerializer
        return ClienteSerializer

    def perform_create(self, serializer):
        if Cliente.objects.filter(usuario=self.request.user).exists():
            raise ValidationError("Ya existe un perfil para este usuario.")
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=["get"])
    def direcciones(self, request, pk=None):
        cliente = self.get_object()
        direcciones = cliente.direcciones.all()
        serializer = DireccionResumenSerializer(direcciones, many=True)
        return Response(serializer.data)


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["ciudad"]
    search_fields = ["calle", "ciudad", "codigo_postal"]
    ordering_fields = ["ciudad", "calle", "id"]
    ordering = ["ciudad", "calle"]

    def get_queryset(self):
        return Direccion.objects.filter(
            cliente__usuario=self.request.user
        ).select_related("cliente")

    def get_serializer_class(self):
        if self.action == "list":
            return DireccionListSerializer
        return DireccionSerializer

    def perform_create(self, serializer):
        cliente = getattr(self.request.user, "cliente", None)

        if cliente is None:
            raise ValidationError(
                "El usuario debe tener un perfil de cliente para registrar direcciones."
            )

        serializer.save(cliente=cliente)

    @action(detail=False, methods=["get"])
    def por_ciudad(self, request):
        ciudad = request.query_params.get("ciudad")

        if not ciudad:
            return Response(
                {"error": "Debes indicar una ciudad mediante el parámetro ciudad."},
                status=400
            )

        direcciones = self.get_queryset().filter(ciudad__iexact=ciudad)
        serializer = DireccionListSerializer(direcciones, many=True)
        return Response(serializer.data)


class ResenaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["producto", "puntuacion"]
    search_fields = [
        "comentario",
        "producto__nombre",
        "cliente__nombre",
        "cliente__apellido",
    ]
    ordering_fields = ["fecha", "puntuacion"]
    ordering = ["-fecha"]

    def get_queryset(self):
        return Resena.objects.select_related(
            "cliente",
            "cliente__usuario",
            "producto"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ResenaListSerializer
        return ResenaSerializer

    def perform_create(self, serializer):
        cliente = getattr(self.request.user, "cliente", None)

        if cliente is None:
            raise ValidationError(
                "Debes tener un perfil de cliente para publicar una reseña."
            )

        serializer.save(cliente=cliente)

    @action(detail=False, methods=["get"])
    def mis_resenas(self, request):
        resenas = self.get_queryset().filter(
            cliente__usuario=request.user
        )

        serializer = ResenaListSerializer(resenas, many=True)
        return Response(serializer.data)
