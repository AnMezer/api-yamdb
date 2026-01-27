from django.urls import path, include
from rest_framework import routers

from constants.constants import FIRST_API_VERSION

urlpatterns = [
    path(FIRST_API_VERSION + '/', include('djoser.urls.jwt'))
]
