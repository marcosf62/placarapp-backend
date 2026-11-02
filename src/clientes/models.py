from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Direccion(models.Model):
    calle = models.CharField(max_length=200)

    def __str__(self):
        return self.calle
