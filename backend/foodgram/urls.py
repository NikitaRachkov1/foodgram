from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from users.views import ObtainEmailAuthToken, LogoutView
from recipes.views import RecipeViewSet
from tags.views import TagViewSet
from ingredients.views import IngredientViewSet
from users.views import UserAvatarView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('api/auth/', include('rest_framework.urls')),
    path(
        'api/auth/token/login/',
        ObtainEmailAuthToken.as_view(),
        name='token_login',
    ),
    path(
        'api/auth/token/logout/',
        LogoutView.as_view(),
        name='token_logout',
    ),
    path(
        'api/users/me/avatar/',
        UserAvatarView.as_view(),
        name='user-avatar',
    ),
    path('api/', include(router.urls)),
]
