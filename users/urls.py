# users/urls.py
from django.urls import include, path
from .views import UsuarioCreateOnlyViewSet, MyTokenObtainPairView, LogoutView, RegisterView
from rest_framework_simplejwt.views import  TokenRefreshView
from rest_framework import routers

router = routers.DefaultRouter()
#router.register(r'users', UserViewSet, basename='users')
router.register(r'users', UsuarioCreateOnlyViewSet, basename='usuarios')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),#registro basico, (hay que cambiar)
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('', include(router.urls)), #CRUD de los usuarios
]
