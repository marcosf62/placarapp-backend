from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categoria


class PermisosCatalogoTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.cliente = User.objects.create_user("cliente", password="x12345678")
        self.staff = User.objects.create_user(
            "staff", password="x12345678", is_staff=True
        )
        Categoria.objects.create(nombre="Placares")

    def test_lectura_es_publica(self):
        resp = self.client.get("/api/categorias/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_anonimo_no_puede_crear(self):
        resp = self.client.post("/api/categorias/", {"nombre": "Mesas"})
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_cliente_no_puede_crear(self):
        self.client.force_authenticate(self.cliente)
        resp = self.client.post("/api/categorias/", {"nombre": "Mesas"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_puede_crear(self):
        self.client.force_authenticate(self.staff)
        resp = self.client.post("/api/categorias/", {"nombre": "Mesas"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_login_devuelve_si_es_staff(self):
        resp = self.client.post(
            "/api/token/", {"username": "staff", "password": "x12345678"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["is_staff"])
        self.assertIn("token", resp.data)
