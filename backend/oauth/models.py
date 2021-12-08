from os import access
from django.db import models


class User(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    accessToken = models.CharField(max_length=256)
    refreshToken = models.CharField(max_length=128)
