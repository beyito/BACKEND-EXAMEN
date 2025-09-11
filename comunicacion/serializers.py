from rest_framework import serializers
from .models import Comunicado

class ComunicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'descripcion', 'fecha_vencimiento', 'tipo', 'administrador', 'activo']
        read_only_fields = ['activo']  # si quieres que siempre se cree activo por default