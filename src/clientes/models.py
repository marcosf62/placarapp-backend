

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cliente"
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Direccion(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="direcciones"
    )
    calle = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad}"


class Resena(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="resenas"
    )
    producto = models.ForeignKey(
        "catalogo.Producto",
        on_delete=models.CASCADE,
        related_name="resenas"
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "producto"],
                name="unique_resena_cliente_producto"
            )
        ]

    def __str__(self):
        return f"Reseña de {self.cliente} - Producto {self.producto_id}"
