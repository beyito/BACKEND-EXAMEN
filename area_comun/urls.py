from rest_framework.routers import DefaultRouter
from .views import AreaComunViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r'areas', AreaComunViewSet, basename='areas')
router.register(r'reservas', ReservaViewSet, basename='reservas')

urlpatterns = router.urls