from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from .yasg import urlpatterns as docs_urls


urlpatterns = docs_urls
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n'),)
]

urlpatterns += i18n_patterns(
    # path('auth/', include('users.urls')),
    path('api/tests/', include('apps.tests_app.urls')),
)
