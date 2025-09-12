from django.urls import path
from . import views

urlpatterns = [
    path('marcarEntrada', views.marcarEntradaVisita, name='marcarEntrada'),
    path('marcarSalida', views.marcarSalidaVisita, name='marcarSalida'),
    path('mostrarCalendarioAreasComunes', views.mostrarCalendarioAreasComunes, name='mostrarCalendarioAreasComunes'),
 #   path('crearListaInvitados<int:copropietario_id>', views.crearListaInvitados, name='crearListaInvitados'),
]