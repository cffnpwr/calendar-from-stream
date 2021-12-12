from django.urls import path

from user.views import UserView

urlpatterns = [
    path('<str:id>/', UserView.as_view())
]
