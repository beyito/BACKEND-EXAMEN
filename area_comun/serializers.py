from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import AreaComun, Reserva
from django.db.models import Q

class AreaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = '__all__'
        
class ReservaSerializer(serializers.ModelSerializer):
    area_comun = serializers.PrimaryKeyRelatedField(queryset=AreaComun.objects.all()) # para asignar area al crear

    class Meta:
        model = Reserva
        fields = '__all__'
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
            Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
        )

        if solapadas.exists():
            raise serializers.ValidationError({
                "Status": 0,
                "Error": 1,
                "message": "Ya existe una reserva en ese horario para esta área.",
                "data": None
            })

        return data
