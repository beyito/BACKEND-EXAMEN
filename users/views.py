from django.shortcuts import render

from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, MyTokenObtainPairSerializer

User = get_user_model()

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
        serializer.is_valid(raise_exception=True)  # si falla, DRF devuelve 401 automáticamente

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
        
