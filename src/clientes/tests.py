import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import TestCase


class EnsureStaffSuperuserTests(TestCase):
    variables = {
        "DJANGO_SUPERUSER_USERNAME": "admin_render",
        "DJANGO_SUPERUSER_PASSWORD": "Clave-Segura-Render-2026!",
        "DJANGO_SUPERUSER_EMAIL": "admin@placarapp.example",
    }

    def ejecutar(self):
        salida = StringIO()
        call_command("ensure_staff_superuser", stdout=salida)
        return salida.getvalue()

    def test_no_crea_usuario_si_no_hay_variables(self):
        with patch.dict(
            os.environ,
            {
                "DJANGO_SUPERUSER_USERNAME": "",
                "DJANGO_SUPERUSER_PASSWORD": "",
                "DJANGO_SUPERUSER_EMAIL": "",
            },
        ):
            self.ejecutar()

        self.assertEqual(get_user_model().objects.count(), 0)

    def test_falla_si_faltan_variables(self):
        with patch.dict(os.environ, self.variables):
            with patch.dict(
                os.environ,
                {"DJANGO_SUPERUSER_EMAIL": ""},
            ):
                with self.assertRaises(CommandError):
                    self.ejecutar()

    def test_crea_superusuario_correctamente(self):
        with patch.dict(os.environ, self.variables):
            self.ejecutar()

        User = get_user_model()
        usuario = User.objects.get(username="admin_render")

        self.assertTrue(usuario.is_staff)
        self.assertTrue(usuario.is_superuser)
        self.assertTrue(
            usuario.check_password(self.variables["DJANGO_SUPERUSER_PASSWORD"])
        )

    def test_no_duplica_ni_cambia_password_al_reiniciar(self):
        User = get_user_model()

        with patch.dict(os.environ, self.variables):
            self.ejecutar()

        usuario = User.objects.get(username="admin_render")
        password_original = usuario.password

        variables_cambiadas = {
            **self.variables,
            "DJANGO_SUPERUSER_PASSWORD": "Otra-Clave-Diferente-2026!",
        }

        with patch.dict(os.environ, variables_cambiadas):
            self.ejecutar()

        usuario.refresh_from_db()

        self.assertEqual(User.objects.filter(username="admin_render").count(), 1)
        self.assertEqual(usuario.password, password_original)

    def test_no_eleva_un_usuario_comun_a_superusuario(self):
        User = get_user_model()
        User.objects.create_user(
            username="admin_render",
            password="Clave-Comun-2026!",
        )

        with patch.dict(os.environ, self.variables):
            with self.assertRaises(CommandError):
                self.ejecutar()

        usuario = User.objects.get(username="admin_render")
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
