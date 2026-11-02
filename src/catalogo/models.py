from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Material(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "materiales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )
    materiales = models.ManyToManyField(Material, related_name="productos")
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nombre} (${self.precio})"