from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import Unidad 
from .serializers import UnidadSerializer
# Create your views here.
import logging #para registrar errores en el servidor

logger = logging.getLogger(__name__)
@api_view(['POST'])
#@permission_classes([IsAuthenticated]) #temporal, cambiar cuando este la auth
@permission_classes([])
def crearUnidad(request):
    """CU03 - Crear nueva unidad
    Solo administradores pueden crear unidades"""
    try:
        # TODO: Validar que el usuario sea administrador cuando esté listo el sistema de auth
        # if request.user.rol != 'administrador':
        #     return Response({
        #         'status': 2,
        #         'error': 1,
        #         'message': 'No tiene permisos para crear unidades',
        #         'data': None
        #     }, status=status.HTTP_403_FORBIDDEN)
        serializer = UnidadSerializer(data=request.data)
        if serializer.is_valid(): 
            #validar unicidad del codigo 
            codigo = serializer.validated_data.get('codigo')
    
            if Unidad.objects.filter(codigo=codigo).exists():
                return Response({
                    'status':2, 
                    'error': 1,
                    'message': 'Ya existe una unidad con ese codigo',
                    'data':None 
                })
            unidad = serializer.save() # crea en la bd

            return Response({
                'status': 1,
                'error': 0,
                'message': f'Unidad {unidad.codigo} creada exitosamente',
                'data': UnidadSerializer(unidad).data
                # ['id',
                # 'codigo',
                #  'bloque',
                # 'piso',
                # 'numero',
                # 'area_m2', 
                # 'estado',
                # tipo_unidad
                # 'created_at', 'updated_at'] 
                # devuelve todo lo que esta en fields del serializador 
            })
        else:
            return Response({
                'status': 2,
                'error': 1,
                'message': 'Datos invalidos para crear la unidad',
                'data': serializer.errors
            })   
    except Exception as e:
        logger.error(f"Error al crear unidad: {str(e)}")
        return Response({
            'status': 2,
            'error': 1,
            'message': 'Error interno del servidor al crear la unidad',
            'data': None
        }) 

@api_view(['PUT'])
#@permission_classes([IsAuthenticated]) #temporal, cambiar cuando este la auth       
@permission_classes([])
def editar_unidad(request, unidad_id):
    """CU04 - Editar unidad existente
    Solo administradores pueden editar unidades"""
    try:
        #TODO: Validar permisos de administrador 
        unidad = Unidad.objects.get(id=unidad_id)
        #Validar que el codigo no este duplicado(excluyendo la unidad actual)
        codigo = request.data.get('codigo')

        if codigo and Unidad.objects.filter(codigo=codigo).exclude(id=unidad_id).exists():
            return Response({
                'status':2, 
                'error': 1,
                'message': 'Ya existe una unidad con ese codigo',
                'data':None 
            }) 
        serializer = UnidadSerializer(unidad, data=request.data, partial=True)
        #partial permite actualizaciones parciales, de algunos campos

        if serializer.is_valid():
            unidad_actualizada = serializer.save()
            return Response({
                'status': 1,
                'error': 0,
                'message': f'Unidad {unidad_actualizada.codigo} actualizada exitosamente',
                'data': UnidadSerializer(unidad_actualizada).data
                # ['id', 
                # 'codigo', 
                # 'bloque', 
                # 'piso',
                #  'numero',
                #  'area_m2', 
                # 'estado', 
                # tipo_unidad
                # 'created_at', 'updated_at'] 
                # devuelve todo lo que esta en fields del serializador 
            }) 
        else:
            return Response({
                'status': 2,
                'error': 1,
                'message': 'Datos invalidos para actualizar la unidad',
                'data': serializer.errors
            })
    except Unidad.DoesNotExist:
        return Response({
            'status': 2,
            'error': 1,
            'message': 'La unidad no encontrada',
            'data': None
        })
    except Exception as e:
        logger.error(f"Error al editar unidad:{unidad_id}: {str(e)}")
        return Response({
            'status': 2,
            'error': 1,
            'message': 'Error interno del servidor al editar la unidad',
            'data': None
        })  

@api_view(["PATCH"])
@permission_classes([])#temporal, cambiar cuando este la auth
def cambiar_estado_unidad(request, unidad_id):
    """CU05 - Cambiar estado de una unidad (activa/inactiva)
    Solo administradores pueden cambiar el estado de las unidades"""
    try:
        #TODO: Validar permisos de administrador
        unidad = Unidad.objects.get(id=unidad_id)
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in ['activa', 'inactiva', 'mantenimiento']:
            return Response({
                'status': 2,
                'error': 1,
                'message': 'Estado invalido. Debe ser "activa", "inactiva" o "mantenimiento"',
                'data': None
            })
        estado_anterior = unidad.estado
        unidad.estado = nuevo_estado
        unidad.save()

        return Response({
            'status': 1,
            'error': 0,
            'message': f'Estado de la unidad {unidad.codigo} cambiado de {estado_anterior} a {nuevo_estado} exitosamente',
            'data': {
                'id_unidad': unidad.id,
                'codigo': unidad.codigo,
                'estado_anterior': estado_anterior,
                'estado_actual': nuevo_estado
            }
        })
    except Unidad.DoesNotExist:
        return Response({
            'status': 2,
            'error': 1,
            'message': 'La unidad no encontrada',
            'data': None
        })
    except Exception as e:
        logger.error(f"Error al cambiar estado de la unidad {unidad_id}: {str(e)}")
        return Response({
            'status': 2,
            'error': 1,
            'message': 'Error interno del servidor al cambiar el estado de la unidad',
            'data': None
        })

@api_view(['GET'])
@permission_classes([])#temporal, cambiar cuando este la auth
def listar_unidades(request):
    """CU03 - Listar todas las unidades con sus detalles"""
    try:
        #TODO: Validar permisos de administrador o copropietario
        unidades = Unidad.objects.all().order_by('bloque', 'piso', 'numero')
        
        # Usar el serializer para convertir los objetos
        serializer = UnidadSerializer(unidades, many=True)
        return Response({
            'status': 1,
            'error': 0,
            'message': f'Se encontraron {len(unidades)} unidades',
            'data': serializer.data
            # ['id',
            #  'codigo',
            #  'bloque', 
            # 'piso', 
            # 'numero', 
            # 'area_m2', 
            # 'estado',
            #  tipo_unidad
            # 'created_at', 'updated_at'] 
                # devuelve todo lo que esta en fields del serializador 
        })
    except Exception as e:
        logger.error(f"Error al listar unidades: {str(e)}")
        return Response({
            'status': 2,
            'error': 1,
            'message': 'Error interno del servidor al listar las unidades',
            'data': None
        })
    
@api_view(['GET'])
@permission_classes([])#temporal, cambiar cuando este la auth
def obtener_unidad(request, unidad_id):
    """CU03 - Obtener detalles de una unidad por su ID"""
    try:
        unidad = Unidad.objects.get(id=unidad_id)
        serializer = UnidadSerializer(unidad)
        return Response({
            'status': 1,
            'error': 0,
            'message': f'Detalles de la unidad {unidad.codigo} obtenidos exitosamente',
            'data': serializer.data
            # ['id', 
            # 'codigo',
            #  'bloque', 
            # 'piso', 
            # 'numero',
            #  'area_m2', 
            # 'estado', 
            # tipo_unidad
            # 'created_at', 'updated_at'] 
             # devuelve todo lo que esta en fields del serializador
        })
    
    except Unidad.DoesNotExist:
        return Response({
            'status': 2,
            'error': 1,
            'message': 'La unidad no encontrada',
            'data': None
        })  
    except Exception as e:
        logger.error(f"Error al obtener unidad {unidad_id}: {str(e)}")
        return Response({
            'status': 2,
            'error': 1,
            'message': 'Error interno del servidor al obtener los detalles de la unidad',
            'data': None
        })