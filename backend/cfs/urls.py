from django.contrib import admin
from django.conf.urls import include, url


urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'auth/', include('oauth.urls')),
    url(r'users/', include('user.urls')),
]
