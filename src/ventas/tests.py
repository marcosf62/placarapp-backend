from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import Categoria, Producto
from clientes.models import Cliente
from logistica.models import Sucursal
from .models import Pedido, DetallePedido, Pago


class VentasApiPermissionsTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="cliente1", password="Clave-Test-2026!"
        )
        self.otro_usuario = User.objects.create_user(
            username="cliente2", password="Clave-Test-2026!"
        )
        self.staff = User.objects.create_user(
            username="staff", password="Clave-Test-2026!", is_staff=True
        )

        self.cliente = Cliente.objects.create(
            usuario=self.usuario,
            nombre="Cliente",
            apellido="Uno",
            email="cliente1@example.test",
        )
        self.otro_cliente = Cliente.objects.create(
            usuario=self.otro_usuario,
            nombre="Cliente",
            apellido="Dos",
            email="cliente2@example.test",
        )

        categoria = Categoria.objects.create(nombre="Muebles test")
        self.producto = Producto.objects.create(
            nombre="Mesa test",
            descripcion="Mesa de prueba",
            precio="10000.00",
            stock=10,
            categoria=categoria,
        )

        self.sucursal = Sucursal.objects.create(
            nombre="Centro",
            direccion="San Martín 123",
            ciudad="Río Cuarto",
        )

        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            tipo_entrega="RETIRO",
            sucursal_retiro=self.sucursal,
            monto_total="10000.00",
        )
        self.otro_pedido = Pedido.objects.create(
            cliente=self.otro_cliente,
            tipo_entrega="RETIRO",
            sucursal_retiro=self.sucursal,
            monto_total="10000.00",
        )

        self.detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=1,
            precio_unitario="10000.00",
        )
        self.otro_detalle = DetallePedido.objects.create(
            pedido=self.otro_pedido,
            producto=self.producto,
            cantidad=1,
            precio_unitario="10000.00",
        )

    def test_cliente_solo_consulta_sus_pedidos(self):
        self.client.force_authenticate(self.usuario)

        respuesta = self.client.get("/api/ventas/pedidos/")

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(
            respuesta.data["results"][0]["id"], self.pedido.id
        )

        propio = self.client.get(
            f"/api/ventas/pedidos/{self.pedido.id}/"
        )
        ajeno = self.client.get(
            f"/api/ventas/pedidos/{self.otro_pedido.id}/"
        )

        self.assertEqual(propio.status_code, status.HTTP_200_OK)
        self.assertEqual(ajeno.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_no_puede_hacer_crud_directo_de_pedidos(self):
        self.client.force_authenticate(self.usuario)

        crear = self.client.post(
            "/api/ventas/pedidos/",
            {"cliente": self.cliente.id, "tipo_entrega": "RETIRO"},
            format="json",
        )
        editar = self.client.patch(
            f"/api/ventas/pedidos/{self.pedido.id}/",
            {"estado": "PAGADO"},
            format="json",
        )
        eliminar = self.client.delete(
            f"/api/ventas/pedidos/{self.pedido.id}/"
        )

        self.assertEqual(crear.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(editar.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(eliminar.status_code, status.HTTP_403_FORBIDDEN)

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, "PENDIENTE")

    def test_cliente_puede_comprar_mediante_checkout(self):
        self.client.force_authenticate(self.usuario)

        respuesta = self.client.post(
            "/api/ventas/pedidos/crear_completo/",
            {
                "tipo_entrega": "RETIRO",
                "sucursal_retiro": self.sucursal.id,
                "productos": [
                    {
                        "producto_id": self.producto.id,
                        "cantidad": 1,
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code, status.HTTP_201_CREATED,
            respuesta.data,
        )
        self.assertEqual(
            Pedido.objects.filter(cliente=self.cliente).count(), 2
        )

    def test_cliente_solo_consulta_sus_detalles(self):
        self.client.force_authenticate(self.usuario)

        respuesta = self.client.get("/api/ventas/detalles/")

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)

        ajeno = self.client.get(
            f"/api/ventas/detalles/{self.otro_detalle.id}/"
        )
        self.assertEqual(ajeno.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_no_puede_crear_editar_ni_borrar_detalles(self):
        self.client.force_authenticate(self.usuario)

        crear = self.client.post(
            "/api/ventas/detalles/",
            {
                "pedido": self.pedido.id,
                "producto": self.producto.id,
                "cantidad": 2,
                "precio_unitario": "10000.00",
            },
            format="json",
        )
        editar = self.client.patch(
            f"/api/ventas/detalles/{self.detalle.id}/",
            {"cantidad": 5},
            format="json",
        )
        eliminar = self.client.delete(
            f"/api/ventas/detalles/{self.detalle.id}/"
        )

        self.assertEqual(crear.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(editar.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(eliminar.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_puede_modificar_pedidos_y_detalles(self):
        self.client.force_authenticate(self.staff)

        editar_pedido = self.client.patch(
            f"/api/ventas/pedidos/{self.pedido.id}/",
            {"estado": "PAGADO"},
            format="json",
        )
        editar_detalle = self.client.patch(
            f"/api/ventas/detalles/{self.detalle.id}/",
            {"cantidad": 2},
            format="json",
        )

        self.assertEqual(editar_pedido.status_code, status.HTTP_200_OK)
        self.assertEqual(editar_detalle.status_code, status.HTTP_200_OK)

    def test_pagos_son_solo_lectura_y_filtrados_por_cliente(self):
        Pago.objects.create(
            pedido=self.pedido,
            metodo="EFECTIVO",
            monto="10000.00",
        )
        Pago.objects.create(
            pedido=self.otro_pedido,
            metodo="EFECTIVO",
            monto="10000.00",
        )

        self.client.force_authenticate(self.usuario)
        respuesta = self.client.get("/api/ventas/pagos/")

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)

        crear = self.client.post(
            "/api/ventas/pagos/",
            {"pedido": self.pedido.id, "metodo": "EFECTIVO", "monto": "10000"},
            format="json",
        )
        self.assertEqual(
            crear.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
