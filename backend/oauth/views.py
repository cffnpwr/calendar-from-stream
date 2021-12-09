import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
import rest_framework_jwt.utils as jwtUtil
import requests

import cfs.settings
from oauth.serializer import UserSerializer
from oauth.models import User


@api_view()
@permission_classes((permissions.AllowAny,))
def googleOAuth2(request):
    data = {
        'code': request.GET.get('code'),
        'client_id': cfs.settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'client_secret': cfs.settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        'redirect_uri': 'http://localhost:5000/auth/google-oauth2/',
        'grant_type': 'authorization_code',
        'access_type': 'offline'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    tokenRes = requests.post(
        'https://www.googleapis.com/oauth2/v4/token', data=data, headers=headers)
    tokenResData = tokenRes.json()

    if tokenRes.status_code == requests.codes.ok:
        userInfoRes = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                                   params={'access_token': tokenResData['access_token']})

        if userInfoRes.status_code == requests.codes.ok:
            userId = userInfoRes.json()['id']
            data = {
                'id': userId,
                'accessToken': tokenResData['access_token'],
                'refreshToken': tokenResData['refresh_token']
            }

            try:
                queryset = User.objects.get(id=userId)
                serializer = UserSerializer(instance=queryset, data=data)

            except:
                serializer = UserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()

                jwtToken = jwtUtil.jwt_encode_handler(
                    {'userId': userId, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)})
                return Response({'token': jwtToken}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(userInfoRes.json(), status=status.HTTP_401_UNAUTHORIZED)

    return Response(tokenResData, status=status.HTTP_401_UNAUTHORIZED)
