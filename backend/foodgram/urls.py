from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from users.views import (LogoutView, ObtainEmailAuthToken,
                         UserAvatarView)


urlpatterns = [
    path('users/', include('users.urls')),
    path('tags/', include('tags.urls')),
    path('recipes/', include('recipes.urls')),
    path('ingredients/', include('ingredients.urls')),
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
