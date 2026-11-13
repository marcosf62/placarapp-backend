from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente
from ventas.models import Pedido
from .models import Envio, Proveedor, Sucursal

BASE = "/api/logistica"


class LogisticaApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester", password="x12345678"
        )
        self.staff = User.objects.create_user(
            username="staff_logistica",
            password="x12345678",
            is_staff=True,
        )

        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombre="Cliente",
            apellido="Test",
            email="cliente@example.test",
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            tipo_entrega="ENVIO",
        )
        self.envio = Envio.objects.create(pedido=self.pedido)

        self.proveedor = Proveedor.objects.create(
            nombre="Maderas del Sur"
        )
        self.sucursal = Sucursal.objects.create(
            nombre="Centro",
            direccion="San Martín 123",
            ciudad="Río Cuarto",
        )

    def test_endpoints_privados_requieren_autenticacion(self):
        for path in ("proveedores", "envios", "movimientos-stock"):
            respuesta = self.client.get(f"{BASE}/{path}/")
            self.assertIn(
                respuesta.status_code,
                (
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_403_FORBIDDEN,
                ),
                path,
            )

    def test_cliente_no_puede_consultar_ni_modificar_logistica(self):
        self.client.force_authenticate(self.user)

        for path in ("proveedores", "envios", "movimientos-stock"):
            respuesta = self.client.get(f"{BASE}/{path}/")
            self.assertEqual(
                respuesta.status_code, status.HTTP_403_FORBIDDEN, path
            )

        crear_proveedor = self.client.post(
            f"{BASE}/proveedores/",
            {"nombre": "Proveedor no autorizado"},
            format="json",
        )
        editar_proveedor = self.client.patch(
            f"{BASE}/proveedores/{self.proveedor.id}/",
            {"nombre": "Modificado"},
            format="json",
        )
        marcar_entregado = self.client.post(
            f"{BASE}/envios/{self.envio.id}/marcar_entregado/",
            {},
            format="json",
        )

        self.assertEqual(
            crear_proveedor.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            editar_proveedor.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            marcar_entregado.status_code, status.HTTP_403_FORBIDDEN
        )

        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.nombre, "Maderas del Sur")

    def test_sucursales_son_publicas_de_lectura(self):
        respuesta = self.client.get(f"{BASE}/sucursales/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        crear = self.client.post(
            f"{BASE}/sucursales/",
            {"nombre": "X"},
            format="json",
        )
        self.assertEqual(
            crear.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_staff_puede_consultar_listados_paginados(self):
        self.client.force_authenticate(self.staff)

        for path in ("proveedores", "envios", "movimientos-stock", "sucursales"):
            respuesta = self.client.get(f"{BASE}/{path}/")
            self.assertEqual(respuesta.status_code, status.HTTP_200_OK, path)
            self.assertIn("results", respuesta.data, path)

    def test_proveedor_list_incluye_movimientos_anidados(self):
        self.client.force_authenticate(self.staff)

        respuesta = self.client.get(f"{BASE}/proveedores/")
        self.assertIn("movimientos", respuesta.data["results"][0])

        detalle = self.client.get(
            f"{BASE}/proveedores/{self.proveedor.pk}/"
        )
        self.assertNotIn("movimientos", detalle.data)

    def test_staff_puede_crear_proveedor(self):
        self.client.force_authenticate(self.staff)

        respuesta = self.client.post(
            f"{BASE}/proveedores/",
            {"nombre": "Herrajes SA"},
            format="json",
        )

        self.assertEqual(
            respuesta.status_code, status.HTTP_201_CREATED
        )
        self.assertTrue(
            Proveedor.objects.filter(nombre="Herrajes SA").exists()
        )

    def test_busqueda_y_filtros_de_proveedores(self):
        self.client.force_authenticate(self.staff)
        Proveedor.objects.create(nombre="Herrajes SA")
        Proveedor.objects.create(nombre="Inactivo SA", activo=False)

        busqueda = self.client.get(
            f"{BASE}/proveedores/?search=maderas"
        )
        filtro = self.client.get(
            f"{BASE}/proveedores/?activo=false"
        )

        self.assertEqual(busqueda.data["count"], 1)
        self.assertEqual(filtro.data["count"], 1)

    def test_action_movimientos_de_proveedor(self):
        self.client.force_authenticate(self.staff)

        respuesta = self.client.get(
            f"{BASE}/proveedores/{self.proveedor.pk}/movimientos/"
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 0)

    def test_staff_puede_marcar_envio_como_entregado(self):
        self.client.force_authenticate(self.staff)

        respuesta = self.client.post(
            f"{BASE}/envios/{self.envio.id}/marcar_entregado/",
            {},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.envio.refresh_from_db()
        self.pedido.refresh_from_db()

        self.assertEqual(self.envio.estado, Envio.Estado.ENTREGADO)
        self.assertEqual(self.pedido.estado, "ENTREGADO")
