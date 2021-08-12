from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from .yasg import urlpatterns as docs_urls

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = docs_urls
urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('api/tests/', include('apps.tests_app.urls')),
    #path('i18n/', include('django.conf.urls.i18n'),)
]

# urlpatterns += i18n_patterns(
#     # path('auth/', include('users.urls')),
    
# )
