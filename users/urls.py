# users/urls.py
from django.urls import include, path
from .views import RegisterView, UserViewSet, MyTokenObtainPairView, LogoutView
from rest_framework_simplejwt.views import  TokenRefreshView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),#registro basico, (hay que cambiar)
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/v1/', include(router.urls)), #CRUD de los usuarios
]
