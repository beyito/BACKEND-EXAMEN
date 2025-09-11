# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    ci = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, default=2)

    # first_name y last_name ya existen en AbstractUser

    def __str__(self):
        return self.username

