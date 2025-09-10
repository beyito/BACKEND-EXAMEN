from django.urls import path
from . import views

urlpatterns = [
    path('marcarEntrada', views.marcarEntradaVisita, name='marcarEntrada'),
    path('marcarSalida', views.marcarSalidaVisita, name='marcarSalida'),
    path('crearComunicado/<int:administrador_id>', views.crearComunicado, name='crearComunicado'),
]