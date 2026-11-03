"""Tests de la app logistica.

Se testea lo que no depende de los modelos de otras apps (Proveedor,
Sucursal y permisos). Los tests de Envio y MovimientoStock con datos reales
se pueden sumar cuando existan Cliente, Direccion y Producto reales
(hace falta crear un Pedido y un Producto válidos).
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Proveedor, Sucursal

BASE = "/api/logistica"


class LogisticaApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="x12345678")
        self.proveedor = Proveedor.objects.create(nombre="Maderas del Sur")
        Sucursal.objects.create(
            nombre="Centro", direccion="San Martín 123", ciudad="Mendoza"
        )

    def test_endpoints_privados_requieren_autenticacion(self):
        for path in ("proveedores", "envios", "movimientos-stock"):
            resp = self.client.get(f"{BASE}/{path}/")
            self.assertIn(
                resp.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
                path,
            )

    def test_sucursales_son_publicas_de_lectura(self):
        resp = self.client.get(f"{BASE}/sucursales/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Solo lectura: no se puede crear por la API.
        resp = self.client.post(f"{BASE}/sucursales/", {"nombre": "X"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_listados_responden_200_y_paginados(self):
        self.client.force_authenticate(self.user)
        for path in ("proveedores", "envios", "movimientos-stock", "sucursales"):
            resp = self.client.get(f"{BASE}/{path}/")
            self.assertEqual(resp.status_code, status.HTTP_200_OK, path)
            self.assertIn("results", resp.data, path)

    def test_proveedor_list_incluye_movimientos_anidados(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(f"{BASE}/proveedores/")
        self.assertIn("movimientos", resp.data["results"][0])
        # En el detalle NO viene anidado.
        detalle = self.client.get(f"{BASE}/proveedores/{self.proveedor.pk}/")
        self.assertNotIn("movimientos", detalle.data)

    def test_crear_proveedor(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            f"{BASE}/proveedores/", {"nombre": "Herrajes SA"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Proveedor.objects.filter(nombre="Herrajes SA").exists())

    def test_busqueda_de_proveedores(self):
        self.client.force_authenticate(self.user)
        Proveedor.objects.create(nombre="Herrajes SA")
        resp = self.client.get(f"{BASE}/proveedores/?search=maderas")
        self.assertEqual(resp.data["count"], 1)

    def test_filtro_de_proveedores_por_activo(self):
        self.client.force_authenticate(self.user)
        Proveedor.objects.create(nombre="Inactivo SA", activo=False)
        resp = self.client.get(f"{BASE}/proveedores/?activo=false")
        self.assertEqual(resp.data["count"], 1)

    def test_action_movimientos_de_proveedor(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(f"{BASE}/proveedores/{self.proveedor.pk}/movimientos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
