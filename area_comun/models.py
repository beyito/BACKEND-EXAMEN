from django.db import models
from users.models import Usuario as User
from django.utils import timezone


class AreaComun(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre_area = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveIntegerField()
    requiere_pago = models.BooleanField(default=False)
    precio_por_bloque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    apertura_hora = models.TimeField()
    cierre_hora = models.TimeField()
    dias_habiles = models.CharField(max_length=50) # Ej: Lunes a Viernes, luego cambiar por tabla horarios
    reglas = models.TextField(blank=True)     
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('ocupado', 'Ocupado'),
        ('libre', 'Libre'),
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo') # luego cambiar estados

    class Meta:
        db_table = 'area_comun'

    def __str__(self):
        return self.nombre_area


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas")
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name="reservas")
    
    fecha = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    
    nota = models.TextField(blank=True)
    creada_en = models.DateTimeField(default=timezone.now)
    cancelada_en = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'reserva'

    def __str__(self):
        return f"{self.area_comun.nombre_area} - {self.usuario.username} ({self.inicio.date()})"
