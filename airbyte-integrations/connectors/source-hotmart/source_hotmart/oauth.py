from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

import requests
from typing import Tuple

class HotmartOauth2Authenticator(Oauth2Authenticator):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ):
        super().__init__(
            "https://api-sec-vlc.hotmart.com/security/oauth/token",
            client_id,
            client_secret,
            refresh_token,
            grant_type="client_credentials"
        )

    def refresh_access_token(self) -> Tuple[str, int]:

        url_params = {
            "grant_type": self.get_grant_type(),
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret()
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.get_refresh_token()
        }

        url = self.get_token_refresh_endpoint()

        response = requests.post(url, headers=headers, params=url_params)
        response.raise_for_status()
        response_body = response.json()
        return response_body[self.get_access_token_name()], response_body[self.get_expires_in_name()]