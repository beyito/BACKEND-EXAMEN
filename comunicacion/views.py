from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Comunicado
from .serializers import ComunicadoSerializer
from users.models import Usuario
# Create your views here.
# CREAR COMUNICADO SOLO LO PUEDE HACER EL ADMINISTRADOR
@api_view(['POST'])
def crearComunicado(request, administrador_id):
    try:
        admin = Usuario.objects.get(id=administrador_id)
        print("Supuesto Admin",admin)
    except Usuario.DoesNotExist:
        return Response({"status": 2, "error": 1, "message": "Usuario no encontrado"})
    
    if not admin.es_admin():
        return Response({"status": 2, "error": 1, "message": "El usuario no es un administrador válido."})
    data = request.data.copy()
    # Pasa el ID, no el objeto
    data['administrador'] = admin.id
    print(data)

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

@api_view(['GET'])
def ListarComunicado(request):
    objetos = Comunicado.objects.filter(activo = False)
    serializer = ComunicadoSerializer(objetos, many=True)
    return Response ({
        "status": 1,
        "errorr": 0,
        "message": "Se crea la lista de comunicados correctamente",
        "value": serializer.data

    })
    
        
        
    