from django.conf.urls import url
from django.urls import path

from user import views

urlpatterns = [
    url(r'login/', views.loginRedirect),
    path(r'<str:id>/', views.UserView.as_view()),
]
