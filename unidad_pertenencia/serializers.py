from rest_framework import serializers
from .models import Unidad

class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = '__all__'
        read_only_fields = ["id", "created_at", "updated_at"]
        
    def validate_codigo(self, value):
            """"Validar que el codigo no este vacio y este en mayusculas"""
            if not value or len(value.strip()) == 0:
                raise serializers.ValidationError("El codigo es obligatorio.")
            return value.strip().upper()
        
    def validate_area_m2(self, value):
            """
            Validar que el area sea un valor positivo
            """ 
            
            if value <= 0:
                raise serializers.ValidationError("El area debe ser un valor positivo.")
            return value