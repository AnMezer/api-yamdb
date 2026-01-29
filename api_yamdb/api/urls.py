from django.urls import path, include
from rest_framework import routers

from constants.constants import FIRST_API_VERSION
from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    TokenViewSet,
    UserViewSet,
    ReviewViewSet,
    CommentViewSet
)

router_v1 = routers.DefaultRouter()
# route_v1.register('auth/signup', TokenViewSet)
# route_v1.register('auth/token', TokenViewSet)
# route_v1.register('users', UserViewSet)
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')

# titles/{title_id}/reviews/
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/',
                   ReviewViewSet, basename='reviews')

# titles/{title_id}/reviews/{review_id}/comments/
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
    CommentViewSet, basename='comments'
)


urlpatterns = [
    # path(FIRST_API_VERSION + '/', include(route_v1.urls))
    path(FIRST_API_VERSION + '/', include('djoser.urls.jwt')),
    path(FIRST_API_VERSION + '/', include(router_v1.urls)),
]
