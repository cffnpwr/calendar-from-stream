from django.urls import path

from oauth import views

urlpatterns = [
    path(r'google-oauth2/', views.googleOAuth2),
]
