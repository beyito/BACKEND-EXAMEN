# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import GuardiaModel

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'ci',
            'phone_number',
            'email',
            'password',   
        ]

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            ci=validated_data.get('ci', ''),
            phone_number=validated_data.get('phone_number', ''),
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])  # 🔑 contraseña encriptada
        user.save()
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Agregar info extra
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email
        data['rol'] = self.user.rol.name
        data['is_staff'] = self.user.is_staff
        return data
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

class GuardiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardiaModel