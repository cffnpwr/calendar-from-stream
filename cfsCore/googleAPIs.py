import requests
import json
import jwt
from jwt.algorithms import RSAAlgorithm
import requests


def refreshAccessToken(clientId, clientSecret, refreshToken):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': clientId,
        'client_secret': clientSecret,
        'refresh_token': refreshToken,
        'grant_type': 'refresh_token'
    }

    res = requests.post(
        'https://www.googleapis.com/oauth2/v4/token', data=data, headers=headers)

    return res.json()


def getNewAccessToken(clientId, clientSecret, refreshToken):
    res = refreshAccessToken(clientId, clientSecret, refreshToken)

    isValid = validateIdToken(
        res['id_token'],
        'https://www.googleapis.com/oauth2/v3/certs',
        'https://accounts.google.com',
        clientId
    )
    if isValid:
        data = {
            'id': isValid['sub'],
            'accessToken': res['access_token'],
            'exp': res['expires_in']
        }

        return data

    return None


def validateIdToken(token, jwksURI, issuer, clientId):
    header = jwt.get_unverified_header(token)
    res = requests.get(jwksURI)

    if res.status_code != requests.codes.ok:
        return None

    jwkSet = res.json()
    jwk = next(filter(lambda k: k['kid'] == header['kid'], jwkSet['keys']))
    pubkey = RSAAlgorithm.from_jwk(json.dumps(jwk))

    decoded = jwt.decode(token, pubkey, issuer=issuer,
                         audience=clientId, algorithms=['RS256'])

    return decoded
