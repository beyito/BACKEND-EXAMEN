from rest_framework import serializers
from .models import GuardiaModel

class GuardiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardiaModel
        fields = '__all__'