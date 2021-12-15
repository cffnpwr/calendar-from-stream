from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'accessToken', 'refreshToken', 'expiryDate', 'urlList')
        extra_kwargs = {
            'accessToken': {'write_only': True},
            'refreshToken': {'write_only': True}
        }
