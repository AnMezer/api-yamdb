from django.urls import path, include
from rest_framework import routers

from constants.constants import FIRST_API_VERSION

from .views import TokenViewSet, UserViewSet


route_v1 = routers.DefaultRouter()
#route_v1.register('auth/signup', TokenViewSet)
#route_v1.register('auth/token', TokenViewSet)
#route_v1.register('users', UserViewSet)

urlpatterns = [
    path(FIRST_API_VERSION + '/', include('djoser.urls.jwt'))
    #path(FIRST_API_VERSION + '/', include(route_v1.urls))
]
