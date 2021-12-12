from django.conf.urls import url

from oauth import views


urlpatterns = [
    url(r'google-oauth2/', views.googleOAuth2),
]
