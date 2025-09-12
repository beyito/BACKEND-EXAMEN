
from django.contrib.auth import authenticate,get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from rest_framework.decorators import api_view, permission_classes, action 
from rest_framework.response import Response
from .serializers import UserSerializer, MyTokenObtainPairSerializer,UsuarioCreateSerializer, UsuarioSerializer,CopropietarioSerializer,CopropietarioLinkCreateSerializer,CopropietarioCreateSerializer
from django.db import transaction 
from .models import Usuario, CopropietarioModel
from rest_framework import generics, viewsets, status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Create your views here.
# Permiso opcional por rol
class IsAdministrador(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, 'user', None)
        return bool(u and u.is_authenticated and getattr(u, 'idRol', None) and u.idRol.name == "Administrador")

class UsuarioCreateOnlyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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

    
    


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Usuario registrado correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Usuarios listados correctamente",
            "data": serializer.data
        })


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({
                "Status": 2,
                "Error": 1,
                "message": "Error al iniciar sesión",
                "data": {}
            }, status=400)
        
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Se inició sesión correctamente",
            "data": serializer.validated_data
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "Status": 1,
                "Error": 0,
                "message": "Se cerro la sesión correctamente",}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({
                "Status": 2,
                "Error": 1,
                "message": "Error al cerrar la sesión",
            },status=status.HTTP_400_BAD_REQUEST)
        
