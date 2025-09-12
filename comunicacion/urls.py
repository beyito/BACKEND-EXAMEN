from django.urls import path
from . import views

urlpatterns = [
    path('crearComunicado/<int:administrador_id>', views.crearComunicado, name='crearComunicado'),
    path('listarComunicados', views.ListarComunicado, name="Listar Comunicado"),
]