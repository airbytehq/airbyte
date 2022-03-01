from typing import Any, Mapping, Optional

import requests
import jwt
import pendulum

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class AppleSearchAdsException(Exception):
    pass

class AppleSearchAdsAuthenticator(TokenAuthenticator):
    audience = 'https://appleid.apple.com'

    expiration_seconds = 60*20

    def __init__(self, client_id: str, team_id: str, key_id: str, private_key: str, algorithm: str = 'ES256'):
        self.client_id = client_id
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = private_key
        self.algorithm = algorithm if algorithm is not None else 'ES256'

        super().__init__(None)

        self._access_token = None
        self._token_expiry_date = pendulum.now()

    def update_access_token(self) -> Optional[str]:
        post_headers = {
            "Host": "appleid.apple.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        post_url = f"https://appleid.apple.com/auth/oauth2/token"

        # Create Client secret
        headers = dict()
        headers['alg'] = self.algorithm
        headers['kid'] = self.key_id

        payload = dict()
        payload['sub'] = self.client_id
        payload['aud'] = self.audience
        payload['iat'] = self._token_expiry_date
        payload['exp'] = pendulum.now().add(seconds=self.expiration_seconds)
        payload['iss'] = self.team_id

        client_secret = jwt.encode(
            payload=payload,
            headers=headers,
            algorithm=self.algorithm,
            key=self.private_key
        )

        post_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": client_secret,
            "scope": "searchadsorg"
        }

        resp = requests.post(post_url,
                    data=post_data,
                    headers=post_headers)
        resp.raise_for_status()

        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry_date = payload['exp']
        return None

    def get_auth_header(self) -> Mapping[str, Any]:
        if self._token_expiry_date < pendulum.now():
            err = self.update_access_token()
            if err:
                raise AppleSearchAdsException(f"auth error: {err}")
        return {"Authorization": f"Bearer {self._access_token}"}
