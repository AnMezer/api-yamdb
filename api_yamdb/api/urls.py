from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from constants.constants import FIRST_API_VERSION
from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    TokenView,
    UserViewSet,
    ReviewViewSet,
    CommentViewSet
)

router_v1 = routers.DefaultRouter()
#route_v1.register('auth/signup', TokenViewSet)
#route_v1.register('auth/token', TokenViewSet)
router_v1.register('users/me', UserViewSet, basename='users_me')
router_v1.register('auth/signup', UserViewSet, basename='signup_user')
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    #path(FIRST_API_VERSION + '/', include(route_v1.urls))
    path(FIRST_API_VERSION + '/' + 'auth/' + 'token/', TokenView.as_view(), name='token_obtain_pair'),
    #path(FIRST_API_VERSION + '/' + 'auth/' + 'signup/', UserViewSet, name='signup_user'),
    #path(FIRST_API_VERSION + '/', include('djoser.urls.jwt')),
    path(FIRST_API_VERSION + '/', include(router_v1.urls)),
]
