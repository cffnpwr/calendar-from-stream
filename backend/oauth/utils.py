import json
import jwt
from jwt.algorithms import RSAAlgorithm
import requests


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
