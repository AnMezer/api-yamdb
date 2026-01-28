from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

User = get_user_model()


class TokenViewSet(TokenObtainPairView, TokenRefreshView):
    pass
    #queryset = User.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    pass
    # queryset = User.objects.all()
    # permission_classes = (permissions.IsAuthenticated)

