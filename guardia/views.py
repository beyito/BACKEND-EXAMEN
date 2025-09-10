from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,authentication_classes,permission_classes 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import MarcarEntradaSerializer, MarcarSalidaSerializer, ComunicadoSerializer
from .models import Usuario

# Create your views here.


# @api_view(['POST']) solo para copropietarios
# def crearVisita(request):
#     """
#     Crea una nueva autorización de visita para un visitante.
#     """
#     # Aquí iría la lógica para crear una nueva autorización de visita
#     return Response({"message": "Funcionalidad de crear visita no implementada aún."}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def crearComunicado(request, administrador_id):
    try:
        admin = Usuario.objects.get(id=administrador_id)
    except Usuario.DoesNotExist:
        return Response({"status": 2, "error": 1, "message": "Usuario no encontrado"})
    
    if not admin.es_admin():
        return Response({"status": 2, "error": 1, "message": "El usuario no es un administrador válido."})
    data = request.data.copy()
    # Pasa el ID, no el objeto
    data['administrador'] = admin.id

    serializer = ComunicadoSerializer(data=data)
    if serializer.is_valid():
        comunicado = serializer.save()  # aquí Django crea el objeto correctamente
        return Response({
            "status": 1,
            "error": 0,
            "message": "Comunicado creado correctamente",
            #"data": ComunicadoSerializer(comunicado).data
        })
    
    return Response({
        "status": 2,
        "error": 1,
        "message": "Error al crear el comunicado",
        "data": serializer.errors
    })



@api_view(['PATCH'])
def marcarEntradaVisita(request):
    serializer = MarcarEntradaSerializer(data=request.data)
    if serializer.is_valid():
        resultado = serializer.save()
        visitante = resultado['visitante']
        registro = resultado['registro']
        return Response({
            "status": 1,
            "error": 0,
            "message": f"Entrada registrada para {visitante.nombre} {visitante.apellido} a las {registro.fecha_entrada}."
        })
    return Response({
        "status": 2,
        "error": 1,
        "message": serializer.errors
    })


@api_view(['PATCH'])
def marcarSalidaVisita(request):
    serializer = MarcarSalidaSerializer(data=request.data)
    if serializer.is_valid():
        resultado = serializer.save()
        visitante = resultado['visitante']
        registro = resultado['registro']
        return Response({
            "status": 1,
            "error": 0,
            "message": f"Salida registrada para {visitante.nombre} {visitante.apellido} a las {registro.fecha_salida}."
        })
    return Response({
        "status": 2,
        "error": 1,
        "message": serializer.errors
    })