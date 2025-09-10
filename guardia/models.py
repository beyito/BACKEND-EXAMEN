from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "rol" 

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    idRol = models.ForeignKey(Rol, on_delete=models.RESTRICT, db_column="idrol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def es_copropietario(self):
         return self.idRol.nombre == "Copropietario"
    
    def es_empleado(self):
         return self.idRol.nombre == "Empleado"
    
    def es_admin(self):
         return self.idRol.nombre == "Administrador"
    
    class Meta:
        db_table = "usuario"
    


class GuardiaModel(models.Model):
    idUsuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="id"
    )
    turno = models.CharField(max_length=50)
    fecha_contratacion = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'guardia'


class CopropietarioModel(models.Model):
    idUsuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="id"
    )
    unidad = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'copropietario'


class PersonaModel(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=50, unique=True)  # CI, pasaporte, etc.
    
    # Relación muchos a muchos: visitante puede visitar a varios copropietarios
    copropietarios = models.ManyToManyField(CopropietarioModel, through="AutorizacionVisita")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        db_table = 'persona'


class AutorizacionVisita(models.Model):
    visitante = models.ForeignKey(PersonaModel, on_delete=models.CASCADE)
    copropietario = models.ForeignKey(CopropietarioModel, on_delete=models.CASCADE)
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, default="Pendiente")

    def __str__(self):
        return f"{self.visitante} autorizado por {self.copropietario} de {self.hora_inicio} a {self.hora_fin}"

    class Meta:
        db_table = 'autorizacion_visita'


class Comunicado(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(max_length=50)  # sin choices
    administrador =  models.ForeignKey(
    Usuario, 
    on_delete=models.CASCADE, 
    db_column='administrador_id'
    )# ID del administrador que crea el comunicado
    activo = models.BooleanField(default=True)

    # def __str__(self):
    #     return f"{self.titulo} ({self.tipo})"

    class Meta:
        db_table = 'comunicado'



class RegistroVisitaModel(models.Model):
    autorizacion = models.ForeignKey(AutorizacionVisita, on_delete=models.CASCADE)
    guardia = models.ForeignKey(GuardiaModel, on_delete=models.CASCADE)
    fecha_entrada = models.DateTimeField(auto_now_add=True, null=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Visita de {self.autorizacion.visitante} a {self.autorizacion.copropietario} registrada por {self.guardia}"

    class Meta:
        db_table = 'registro_visita'
