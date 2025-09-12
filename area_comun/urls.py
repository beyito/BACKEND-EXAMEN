from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r'areas', views.AreaComunViewSet, basename='areas') # crud de areas
router.register(r'reservas', views.ReservaViewSet, basename='reservas') #crud de reservas

urlpatterns = router.urls

urlpatterns = [
    path('marcarEntrada', views.marcarEntradaVisita, name='marcarEntrada'),
    path('marcarSalida', views.marcarSalidaVisita, name='marcarSalida'),
    path('mostrarCalendarioAreasComunes', views.mostrarCalendarioAreasComunes, name='mostrarCalendarioAreasComunes'),
 #   path('crearListaInvitados<int:copropietario_id>', views.crearListaInvitados, name='crearListaInvitados'),
]
