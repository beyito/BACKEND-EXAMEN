from django.urls import path
from . import views

urlpatterns = [
    path('unidades', views.listar_unidades, name='listar_unidades'),
    path('unidades/crear', views.crearUnidad, name='crear_unidad'),
    path('unidades/<int:unidad_id>', views.obtener_unidad, name='obtener_unidad'),
    path('unidades/<int:unidad_id>/editar', views.editar_unidad, name='editar_unidad'),
    path('unidades/<int:unidad_id>/estado',views.cambiar_estado_unidad,name='cambiar_estado_unidad'),
]
