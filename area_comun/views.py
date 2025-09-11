from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import AreaComun, Reserva
from .serializers import AreaComunSerializer, ReservaSerializer
from django.utils import timezone


class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        areas = self.get_queryset()
        serializer = self.get_serializer(areas, many=True)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Áreas listadas correctamente",
            "data": serializer.data
        })
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.rol_id != 1:
            return Response({
                "Status": 0,
                "Error": 1,
                "message": "No tienes permisos para eliminar áreas comunes",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.activa = False
        instance.estado = 'inactivo'
        instance.save()

        return Response({
            "Status": 1,
            "Error": 0,
            "message": f"Área con id {instance.pk} eliminada correctamente",
            "data": {}
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        #Validar si es Admin
        if not request.user.is_authenticated or request.user.rol_id != 1:
            return Response({
                "Status": 0,
                "Error": 1,
                "message": "No tienes permisos para crear áreas comunes",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Área creada correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        reservas = self.get_queryset()
        serializer = self.get_serializer(reservas, many=True)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Reservas listadas correctamente",
            "data": serializer.data
        })

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Reserva creada correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado == 'cancelada':
            return Response({
                "Status": 2,
                "Error": 1,
                "message": "La reserva ya está cancelada",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        motivo = request.data.get('motivo_cancelacion', '')
        reserva.estado = 'cancelada'
        reserva.cancelada_en = timezone.now()
        reserva.motivo_cancelacion = motivo
        reserva.save()

        serializer = self.get_serializer(reserva)
        return Response({
            "Status": 1,
            "Error": 0,
            "message": "Reserva cancelada correctamente",
            "data": serializer.data
        })