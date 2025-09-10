from rest_framework import serializers
from .models import GuardiaModel,AutorizacionVisita, RegistroVisitaModel, PersonaModel, GuardiaModel, Usuario, Comunicado

class GuardiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardiaModel
        fields = '__all__'

class ListaVisitantesSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    fecha_visita = serializers.DateField()
    hora_entrada = serializers.TimeField()
    hora_salida = serializers.TimeField()

    class Meta:
        fields = ['nombre', 'apellido', 'fecha_visita', 'hora_entrada', 'hora_salida']

class ComunicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'descripcion', 'fecha_vencimiento', 'tipo', 'administrador', 'activo']
        read_only_fields = ['activo']  # si quieres que siempre se cree activo por default

    # Validación personalizada del administrador
    # def validate(self, data):
    #     from .models import Usuario
    #     try:
    #         admin = Usuario.objects.get(id=data['administrador_id'])
    #         if not admin.es_admin():
    #             raise serializers.ValidationError("El usuario no es un administrador válido.")
    #     except Usuario.DoesNotExist:
    #         raise serializers.ValidationError("Administrador no encontrado.")
    #     return data
      

    # def create(self, validated_data):
    #     from .models import Comunicado, Usuario
    #     print("claidate data")
    #     print(validated_data)
    #     admin = Usuario.objects.get(id=validated_data['administrador'])
    #     #print("HOLA ESTE EL AEL ADMIN ID"+admin.id)
    #     print("validate data: ")
    #     print(validated_data)
    #     comunicado = Comunicado.objects.create(
    #         titulo=validated_data['titulo'],
    #         descripcion=validated_data['descripcion'],
    #         fecha_vencimiento=validated_data.get('fecha_vencimiento'),
    #         tipo=validated_data['tipo'],
    #         administrador_id=validated_data['administrador'],
    #     )
    #     return comunicado

class MarcarEntradaSerializer(serializers.Serializer):
    guardia_id = serializers.IntegerField()
    autorizacion_id = serializers.IntegerField()

    def validate(self, data):
        print(data)
        print(data['autorizacion_id'])
        autorizacion = AutorizacionVisita.objects.filter(id=data['autorizacion_id']).first()
        guardia = GuardiaModel.objects.filter(idUsuario=data['guardia_id']).first()
        print (autorizacion)
        print(guardia)
        
        if not autorizacion or autorizacion.estado != "Pendiente":
            raise serializers.ValidationError("No hay una autorización válida en este momento.")
        data['autorizacion'] = autorizacion
        return data

    def save(self):
        autorizacion = self.validated_data['autorizacion']
        guardia = GuardiaModel.objects.get(idUsuario=self.validated_data['guardia_id'])
        visitante = PersonaModel.objects.get(id=autorizacion.visitante_id)

        from django.utils import timezone
        ahora = timezone.now()

        registro = RegistroVisitaModel.objects.create(
            autorizacion=autorizacion,
            guardia=guardia,
            fecha_entrada=ahora,
            fecha_salida=None
        )

        autorizacion.estado = "En Visita"
        autorizacion.save()

        return {
            "visitante": visitante,
            "registro": registro
        }


class MarcarSalidaSerializer(serializers.Serializer):
    autorizacion_id = serializers.IntegerField()

    def validate(self, data):
        autorizacion = AutorizacionVisita.objects.filter(id=data['autorizacion_id']).first()
        if not autorizacion:
            raise serializers.ValidationError("Autorización no encontrada.")
        data['autorizacion'] = autorizacion

        registro = RegistroVisitaModel.objects.filter(
            autorizacion=autorizacion,
            fecha_entrada__isnull=False,
            fecha_salida__isnull=True
        ).first()
        if not registro:
            raise serializers.ValidationError("No hay un registro de visita activo para este visitante.")
        data['registro'] = registro
        return data

    def save(self):
        registro = self.validated_data['registro']
        autorizacion = self.validated_data['autorizacion']

        from django.utils import timezone
        ahora = timezone.now()

        registro.fecha_salida = ahora
        registro.save()

        autorizacion.estado = "Completada"
        autorizacion.save()

        visitante = PersonaModel.objects.get(id=autorizacion.visitante_id)

        return {
            "visitante": visitante,
            "registro": registro
        }
