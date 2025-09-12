from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import AutorizacionVisita, RegistroVisitaModel, AreaComun, Reserva
from users.models import GuardiaModel, PersonaModel
from django.db.models import Q


# CALNEDARIO AREA COMUNES
class AreaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = '_all_'

class RegistroVisita(serializers.ModelSerializer):
    class Meta:
        model = RegistroVisitaModel
        fields = '_all_'

class ReservaSerializer(serializers.ModelSerializer):
    # usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # para asignar usuario al crear
    area_comun = serializers.PrimaryKeyRelatedField(queryset=AreaComun.objects.all()) # para asignar area al crear

    class Meta:
        model = Reserva
        fields = '_all_'
        read_only_fields = ['usuario']

    def validate(self, data):
        fecha = data['fecha']
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']
        area = data['area_comun']

        # Combina fecha y hora
        inicio_datetime = datetime.combine(fecha, hora_inicio)
        fin_datetime = datetime.combine(fecha, hora_fin)

        # Convierte a datetime con zona horaria local
        inicio_datetime = timezone.make_aware(inicio_datetime, timezone.get_current_timezone())
        fin_datetime = timezone.make_aware(fin_datetime, timezone.get_current_timezone())

        ahora_local = timezone.localtime()  # Hora local del servidor
        # print("fecha:", ahora_local.date())
        # print("hora:", ahora_local.time())

        # Validación 24 horas antes
        if inicio_datetime < ahora_local + timedelta(hours=24):
            raise serializers.ValidationError({
                "Status": 0,
                "Error": 1,
                "message": "Las reservas deben realizarse al menos 24 horas antes.",
                "data": None
            })

        # Validar que fin > inicio
        if fin_datetime <= inicio_datetime:
            raise serializers.ValidationError({
                "Status": 0,
                "Error": 1,
                "message": "La hora de fin debe ser posterior a la hora de inicio.",
                "data": None
            })

        # Validar solapamiento con otras reservas
        solapadas = Reserva.objects.filter(
            area_comun=area,
            fecha=fecha
        ).filter(
            Q(hora_inicio_lt=hora_fin) & Q(hora_fin_gt=hora_inicio)
        )

        if solapadas.exists():
            raise serializers.ValidationError({
                "Status": 0,
                "Error": 1,
                "message": "Ya existe una reserva en ese horario para esta área.",
                "data": None
            })

        return data
    
# REGISTRO DE VISITAS

class ListaVisitantesSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    fecha_visita = serializers.DateField()
    hora_entrada = serializers.TimeField()
    hora_salida = serializers.TimeField()

    class Meta:
        fields = ['nombre', 'apellido', 'fecha_visita', 'hora_entrada', 'hora_salida']

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