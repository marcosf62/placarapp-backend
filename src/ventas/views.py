from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from catalogo.models import Producto
from clientes.models import Direccion
from logistica.models import Sucursal

from .models import Pedido, DetallePedido, Pago
from .serializers import (
    PedidoSerializer,
    DetallePedidoSerializer,
    PagoSerializer,
)


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["estado", "tipo_entrega", "cliente__nombre"]
    ordering_fields = ["fecha_venta", "monto_total"]

    def get_queryset(self):
        queryset = Pedido.objects.all().order_by("-fecha_venta")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(cliente__usuario=self.request.user)

    @action(detail=False, methods=["post"], url_path="crear_completo")
    def crear_completo(self, request):
        cliente = getattr(request.user, "cliente", None)

        if cliente is None:
            return Response(
                {"error": "El usuario no tiene un perfil de cliente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        productos = request.data.get("productos", [])
        tipo_entrega = request.data.get("tipo_entrega")

        if not isinstance(productos, list) or not productos:
            return Response(
                {"error": "El pedido debe contener productos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo_entrega not in ["RETIRO", "ENVIO"]:
            return Response(
                {"error": "Tipo de entrega inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():

                direccion = None
                sucursal = None

                if tipo_entrega == "ENVIO":
                    datos_direccion = request.data.get("direccion_envio")

                    if not isinstance(datos_direccion, dict):
                        return Response(
                            {"error": "Debés indicar los datos de la dirección."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    campos = ["calle", "numero", "ciudad", "codigo_postal"]

                    if any(
                        not str(datos_direccion.get(campo, "")).strip()
                        for campo in campos
                    ):
                        return Response(
                            {"error": "Todos los campos de la dirección son obligatorios."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    direccion = Direccion.objects.create(
                        cliente=cliente,
                        calle=str(datos_direccion["calle"]).strip(),
                        numero=str(datos_direccion["numero"]).strip(),
                        ciudad=str(datos_direccion["ciudad"]).strip(),
                        codigo_postal=str(datos_direccion["codigo_postal"]).strip(),
                    )

                else:
                    sucursal_id = request.data.get("sucursal_retiro")

                    if not sucursal_id:
                        return Response(
                            {"error": "Debés indicar una sucursal de retiro."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    try:
                        sucursal = Sucursal.objects.get(
                            pk=sucursal_id,
                            activo=True,
                        )
                    except (Sucursal.DoesNotExist, ValueError, TypeError):
                        return Response(
                            {"error": "La sucursal no existe o no está activa."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                pedido = Pedido.objects.create(
                    cliente=cliente,
                    tipo_entrega=tipo_entrega,
                    direccion_envio=direccion,
                    sucursal_retiro=sucursal,
                    monto_total=Decimal("0.00"),
                )

                total = Decimal("0.00")

                for item in productos:
                    if not isinstance(item, dict):
                        raise ValueError("Formato de producto inválido.")

                    producto_id = item.get("producto_id")
                    cantidad_recibida = item.get("cantidad")

                    if producto_id is None or cantidad_recibida is None:
                        raise ValueError("Faltan datos del producto.")

                    if isinstance(cantidad_recibida, bool):
                        raise ValueError("La cantidad debe ser un número entero.")

                    try:
                        cantidad_decimal = Decimal(str(cantidad_recibida))
                    except (InvalidOperation, TypeError, ValueError):
                        raise ValueError("La cantidad debe ser un número entero.")

                    if (
                        not cantidad_decimal.is_finite()
                        or cantidad_decimal != cantidad_decimal.to_integral_value()
                    ):
                        raise ValueError("La cantidad debe ser un número entero.")

                    cantidad = int(cantidad_decimal)

                    if cantidad <= 0:
                        raise ValueError("La cantidad debe ser mayor que cero.")

                    try:
                        producto = Producto.objects.get(
                            pk=producto_id,
                            activo=True,
                        )
                    except (Producto.DoesNotExist, ValueError, TypeError):
                        raise ValueError(
                            "Uno de los productos no existe o no está activo."
                        )

                    actualizado = Producto.objects.filter(
                        pk=producto.pk,
                        activo=True,
                        stock__gte=cantidad,
                    ).update(stock=F("stock") - cantidad)

                    if actualizado == 0:
                        raise ValueError(
                            f"Stock insuficiente para el producto {producto.nombre}."
                        )

                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                    )

                    total += producto.precio * cantidad

                pedido.monto_total = total
                pedido.save(update_fields=["monto_total"])

        except (ValueError, InvalidOperation, TypeError, KeyError) as error:
            return Response(
                {"error": str(error) or "Los datos del pedido son inválidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED,
        )


class DetallePedidoViewSet(viewsets.ModelViewSet):
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = DetallePedido.objects.all().order_by("id")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(pedido__cliente__usuario=self.request.user)


class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pago.objects.all().order_by("-fecha_monto", "-id")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(pedido__cliente__usuario=self.request.user)
