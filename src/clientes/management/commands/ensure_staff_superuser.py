import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea el superusuario inicial de Render si todavía no existe."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        configuracion = (username, password, email)

        if not any(configuracion):
            self.stdout.write(
                "No se configuraron credenciales de superusuario. "
                "Se omite la inicialización."
            )
            return

        if not all(configuracion):
            raise CommandError(
                "Debés configurar las tres variables: "
                "DJANGO_SUPERUSER_USERNAME, "
                "DJANGO_SUPERUSER_PASSWORD y DJANGO_SUPERUSER_EMAIL."
            )

        User = get_user_model()
        username_field = User.USERNAME_FIELD

        usuario = User._default_manager.filter(
            **{username_field: username}
        ).first()

        if usuario:
            if usuario.is_staff and usuario.is_superuser:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"El superusuario '{username}' ya existe. "
                        "No se modificaron sus credenciales."
                    )
                )
                return

            raise CommandError(
                f"Ya existe '{username}', pero no es superusuario. "
                "No se modificaron sus permisos."
            )

        usuario_nuevo = User(
            **{
                username_field: username,
                User.EMAIL_FIELD: email,
            }
        )

        try:
            validate_password(password, user=usuario_nuevo)
        except ValidationError as error:
            raise CommandError(
                "La contraseña configurada no cumple los requisitos: "
                + "; ".join(error.messages)
            ) from error

        User._default_manager.create_superuser(
            **{
                username_field: username,
                User.EMAIL_FIELD: email,
                "password": password,
            }
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario '{username}' creado correctamente."
            )
        )
