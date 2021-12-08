from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'auth/', include('oauth.urls'))
]
