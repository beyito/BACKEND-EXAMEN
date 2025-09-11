from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from .models import AreaComun, Reserva
from .serializers import MarcarEntradaSerializer, MarcarSalidaSerializer

# Create your views here.
@api_view(['GET'])
def mostrarCalendarioAreasComunes(request):
    # Obtener fecha del body
    fecha_str = request.data.get("fecha")
    if not fecha_str:
        return Response({
            "status": 2,
            "error": 1,
            "message": "Debe enviar una fecha en formato YYYY-MM-DD",
        })

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            "status": 2,
            "error": 1,
            "message": "Formato de fecha inválido, use YYYY-MM-DD",
        })

    data = {"disponibles": [], "ocupados": []}

    for area in AreaComun.objects.all():
        # Obtener horario de apertura/cierre de la zona
        horario_inicio = timezone.make_aware(datetime.combine(fecha, area.apertura_hora))
        horario_fin = timezone.make_aware(datetime.combine(fecha, area.cierre_hora))

        # Traer reservas del día
        reservas = Reserva.objects.filter(
            area_comun=area,
            fecha=fecha,
            estado='confirmada'  # Solo considerar reservas confirmadas
        ).order_by("hora_inicio")

        ocupados = []
        libres = []
        current_time = horario_inicio

        for r in reservas:
            # Combinar fecha y hora para datetime aware
            inicio_dt = timezone.make_aware(datetime.combine(r.fecha, r.hora_inicio))
            fin_dt = timezone.make_aware(datetime.combine(r.fecha, r.hora_fin))

            # Añadir a ocupados
            ocupados.append({
                "hora_inicio": inicio_dt.strftime("%H:%M"),
                "hora_fin": fin_dt.strftime("%H:%M")
            })

            # Hueco libre antes de esta reserva
            if inicio_dt > current_time:
                libres.append({
                    "hora_inicio": current_time.strftime("%H:%M"),
                    "hora_fin": inicio_dt.strftime("%H:%M")
                })

            # Avanzar current_time al final de la reserva
            if fin_dt > current_time:
                current_time = fin_dt

        # Último hueco hasta cierre del área
        if current_time < horario_fin:
            libres.append({
                "hora_inicio": current_time.strftime("%H:%M"),
                "hora_fin": horario_fin.strftime("%H:%M")
            })

        data["ocupados"].append({"area_comun": area.nombre_area, "horarios": ocupados})
        data["disponibles"].append({"area_comun": area.nombre_area, "horarios": libres})

    return Response({
        "status": 1,
        "error": 0,
        "message": "Calendario de áreas comunes",
        "data": data
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
