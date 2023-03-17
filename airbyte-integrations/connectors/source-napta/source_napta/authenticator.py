from typing import Any, Mapping, Tuple

import requests
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator


class NaptaAuthenticator(Oauth2Authenticator):
    def __init__(self, client_id: str, client_secret: str, token_refresh_endpoint: str):
        super().__init__(
            token_refresh_endpoint=token_refresh_endpoint, client_id=client_id, client_secret=client_secret, refresh_token=client_secret
        )

    # Napta has a very weird way to refresh and give access tokens
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = {
            "grant_type": "client_credentials",
            "audience": "backend",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return payload

    def get_request_headers(self) -> Mapping[str, Any]:
        headers = {"content-type": "application/json", "Authorization": f"Bearer {self.get_access_token()}"}
        return headers

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                auth=(self.client_id, self.client_secret),
            )

            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}")
