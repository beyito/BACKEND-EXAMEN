from rest_framework import serializers
from .models import GuardiaModel, Usuario, ResidenteModel, CopropietarioModel, PersonaModel, Rol
from django.db import transaction, IntegrityError
from django.utils import timezone

class GuardiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardiaModel
        fields = '__all__'

class UsuarioMinSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(source='idRol.name', read_only=True)
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'ci', 'telefono', 'rol']
        read_only_fields = ['id']

class UsuarioCreateSerializer(serializers.ModelSerializer):
    idRol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'password', 'nombre', 'first_name', 'last_name', 'email', 'ci', 'telefono', 'idRol']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate_username(self, value):
            v = (value or '').strip()
            if not v:
                raise serializers.ValidationError("El nombre de usuario es obligatorio.")
            if Usuario.objects.filter(username=v).exists():
                raise serializers.ValidationError("El nombre de usuario ya está en uso.")
            return v
    def validate_email(self, value):
            v = (value or '').strip()
            if not v:
                raise serializers.ValidationError("El correo electrónico es obligatorio.")
            if Usuario.objects.filter(email=v).exists():
                raise serializers.ValidationError("El correo electrónico ya está en uso.")
            return v
    def validate_ci(self, value):
            v = (value or '').strip()
            if not v:
                raise serializers.ValidationError("La cédula de identidad es obligatoria.")
            if Usuario.objects.filter(ci=v).exists():
                raise serializers.ValidationError("La cédula de identidad ya está en uso.")
            return v
    def create(self, validated_data):
            password = validated_data.pop('password')
            user = Usuario.objects.create(**validated_data, password=password)
            return user

class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(source='idRol.name', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'first_name', 'last_name', 
                  'email', 'ci', 'telefono', 'estado', 'rol', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at','estado']            
#-------- Lectura de Copropietario----------------------
class CopropietarioSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='idUsuario_id', read_only=True)
    usuario = UsuarioMinSerializer(source='idUsuario', read_only=True)
    class Meta:
        model = CopropietarioModel
        fields = ['id','usuario','unidad', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
#---------creacion de copropietario (usuario + copropietarioModel) ----------------------
class CopropietarioCreateSerializer(serializers.Serializer):
    #  campos para Usuario (Abstactuser)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    nombre = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    ci = serializers.CharField(max_length=20)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    # campos para CopropietarioModel
    unidad = serializers.CharField(max_length=50)

    def validate_username(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")
        if Usuario.objects.filter(username=v).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return v
    def validate_email(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError("El correo electrónico es obligatorio.")
        if Usuario.objects.filter(email=v).exists():
            raise serializers.ValidationError("El correo electrónico ya está en uso.")
        return v
    def validate_ci(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError("La cédula de identidad es obligatoria.")
        if Usuario.objects.filter(ci=v).exists():
            raise serializers.ValidationError("La cédula de identidad ya está en uso.")
        return v
    def validate_unidad(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError("La unidad es obligatoria.")
        return v
    @transaction.atomic
    def create(self, validated_data):
        try:
            
            with transaction.atomic():
                rol, _ = Rol.objects.get_or_create(name="Copropietario")
                user = Usuario.objects.create_user(
                    ci=validated_data['ci'],
                    username=validated_data['username'],
                    nombre=validated_data['nombre'],
                    email=validated_data['email'],
                    telefono=validated_data.get('telefono', ''),
                    password=validated_data['password'],
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                    idRol=rol 
                )
                cop  = CopropietarioModel.objects.create(
                    idUsuario=user,
                    unidad=validated_data['unidad']
                )
                return cop
        except IntegrityError:
            raise serializers.ValidationError("Error al crear el copropietario.")

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaModel 
        fields = ['id', 'nombre', 'apellido', 'documento']
        read_only_fields = ['id']

    def validate_documento(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El documento es obligatorio.")
        return value.strip()
    def validate_nombre(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value.title()

class ResidenteSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    copropietario_id = serializers.IntegerField(source='idCopropietario_id', read_only=True)
    class Meta:
        model = ResidenteModel
        fields = [
            'id', 'persona', 'copropietario_id', 'tipo',
            'fecha_inicio', 'fecha_fin', 'email_contacto',
            'created_at', 'updated_at'
        ]

class CopropietarioLinkCreateSerializer(serializers.Serializer):
    #datos a enviar 
    idUsuario = serializers.IntegerField()
    unidad = serializers.CharField(max_length=50)

    def validate(self, attrs):
        user_id = attrs.get('idUsuario')
        unidad = (attrs.get('unidad') or '').strip()
        if not unidad:
            raise serializers.ValidationError({"unidad":"La unidad es obligatoria"})
        #usuario existe
        try:
            user = Usuario.objects.select_related('idRol').get(id=user_id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"idUsuario":"El usuario no encontrado"})
        #no duplicar onetoone
        if CopropietarioModel.objects.filter(idUsuario=user.id).exists():
            raise serializers.ValidationError({"idUsuario":"El usuario ya es copropietario"})
        # decide tu politica
        # a) estricto: exigir rol copropietario
        if not user.idRol or user.idRol.name != "Copropietario":
            raise serializers.ValidationError({"idUsuario":"El usuario no tiene rol copropietario"})
        attrs['user'] = user
        attrs['unidad'] = unidad
        return attrs
    @transaction.atomic
    def create(self, validated_data):
        user = validated_data['user']
        unidad = validated_data['unidad']
        return CopropietarioModel.objects.create(idUsuario=user, unidad=unidad)
        
