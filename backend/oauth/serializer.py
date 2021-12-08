from django.db.models.fields import Field
from rest_framework import serializers
from oauth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'accessToken', 'refreshToken')
