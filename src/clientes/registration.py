from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cliente


class RegistroClienteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=100, trim_whitespace=True)
    apellido = serializers.CharField(max_length=100, trim_whitespace=True)
    telefono = serializers.CharField(
        max_length=30, required=False, allow_blank=True
    )
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    def validate_username(self, value):
        User = get_user_model()
        campo = User.USERNAME_FIELD

        if User._default_manager.filter(
            **{f"{campo}__iexact": value}
        ).exists():
            raise serializers.ValidationError(
                "Este nombre de usuario ya está registrado."
            )
        return value

    def validate_email(self, value):
        User = get_user_model()

        if User._default_manager.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Este correo electrónico ya está registrado."
            )
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas no coinciden."
            })

        User = get_user_model()
        usuario = User(
            username=attrs["username"],
            email=attrs["email"],
        )

        try:
            validate_password(attrs["password"], user=usuario)
        except DjangoValidationError as error:
            raise serializers.ValidationError({
                "password": error.messages
            }) from error

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        User = get_user_model()
        campo = User.USERNAME_FIELD

        datos = {
            campo: validated_data["username"],
            "email": validated_data["email"],
            "password": validated_data["password"],
            "is_staff": False,
            "is_superuser": False,
        }

        usuario = User._default_manager.create_user(**datos)

        Cliente.objects.create(
            usuario=usuario,
            nombre=validated_data["nombre"],
            apellido=validated_data["apellido"],
            email=validated_data["email"],
            telefono=validated_data.get("telefono", ""),
        )

        return usuario


class RegistroClienteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistroClienteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        return Response(
            {
                "mensaje": "Cuenta creada correctamente. Ya podés iniciar sesión.",
                "usuario": usuario.get_username(),
            },
            status=status.HTTP_201_CREATED,
        )
