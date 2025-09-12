from django.shortcuts import render
from django.auth import authenticate 
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from rest_framework.decorators import api_view, permission_classes, action 
from rest_framework.response import Response
from .serializers import UsuarioCreateSerializer, UsuarioSerializer,CopropietarioSerializer,CopropietarioLinkCreateSerializer,CopropietarioCreateSerializer
from django.db import transaction 
from .models import Usuario, CopropietarioModel

# Create your views here.
# Permiso opcional por rol
class IsAdministrador(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, 'user', None)
        return bool(u and u.is_authenticated and getattr(u, 'idRol', None) and u.idRol.name == "Administrador")

class UsuarioCreateOnlyViewSet(maxins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Usuario.objects.none()
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get_permission(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(),IsAdministrador]
        if self.action in ['registrar_copropietario', 'vincular_copropietario']:
            return [IsAuthenticated(),IsAdministrador]
        return [IsAuthenticated()]
    

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        
    # Registrar Usuario
    def create(self, request, *args, **kwargs):
        ser = UsuarioCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response({
                "Status": 2,
                "Error": 1,
                "message": "Datos inválidos",
                "data": {"errors": ser.errors},
                "result": None
            })
        user = ser.save()
        out = UsuarioSerializer(user).data
        return Response({
            "Status": 1,
            "Error": 0,
            "message": f"Usuario registrado id={user.id}",
            "data": {"id": user.id},
            "result": out
        })
    # Registrar Copropietario (Crea Usuario + Copropietario)
    @action(detail=False, methods=['post'], url_path='registrar-copropietario')
    @transaction.atomic
    def registrar_copropietario(self, request):
        ser = CopropietarioCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response({
                "Status": 2,
                "Error": 1,
                "message": "Datos inválidos",
                "data": {"errors": ser.errors},
                "result": None
            })
        cop = ser.save()
        out = CopropietarioSerializer(cop).data
        return Response({
            "Status": 1,
            "Error": 0,
            "message": f"Copropietario registrado idUsuario={cop.idUsuario_id}",
            "data": {"idUsuario": cop.idUsuario_id, "unidad": cop.unidad},
            "result": out
        })

    
    