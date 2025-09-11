from django.db import models

# Create your models here.
class Unidad(models.Model):
    # Opciones para tipo_unidad
    TIPOS_UNIDAD = [
        ('apartamento', 'Apartamento'),
        ('casa', 'Casa'),
        ('local', 'Local Comercial'),
        ('oficina', 'Oficina'),
        ('deposito', 'Depósito'),
        ('parqueadero', 'Parqueadero'),
        ('otro', 'Otro'),
    ]
    codigo = models.CharField(max_length=20, unique=True)
    bloque = models.CharField(max_length=10)
    piso = models.IntegerField()
    numero = models.CharField(max_length=10)
    area_m2 = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(max_length=20, default = 'activa')
    tipo_unidad = models.CharField(
        max_length=20, 
        choices=TIPOS_UNIDAD, 
        default='apartamento',
        help_text='Tipo de unidad'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta: 
        db_table = 'unidad'
    
    def __str__(self):
        return f"Unidad {self.codigo} - Bloque {self.bloque}, Piso {self.piso}, Numero {self.numero}"