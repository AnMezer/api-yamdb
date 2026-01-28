from django.urls import path, include
from rest_framework import routers

from constants.constants import FIRST_API_VERSION
from .views import CategoryViewSet, GenreViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = [
    path(FIRST_API_VERSION + '/', include('djoser.urls.jwt')),
    path(FIRST_API_VERSION + '/', include(router_v1.urls)),
]
