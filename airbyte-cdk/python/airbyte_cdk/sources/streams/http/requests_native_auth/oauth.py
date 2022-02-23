#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Tuple

import pendulum
import requests
from requests.auth import AuthBase


class Oauth2Authenticator(AuthBase):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.
    """

    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        scopes: List[str] = None,
        token_expiry_date: pendulum.datetime = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
    ):
        self.token_refresh_endpoint = token_refresh_endpoint
        self.client_secret = client_secret
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.scopes = scopes
        self.access_token_name = access_token_name
        self.expires_in_name = expires_in_name

        self._token_expiry_date = token_expiry_date or pendulum.now().subtract(days=1)
        self._access_token = None

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def get_access_token(self):
        if self.token_has_expired():
            t0 = pendulum.now()
            token, expires_in = self.refresh_access_token()
            self._access_token = token
            self._token_expiry_date = t0.add(seconds=expires_in)

        return self._access_token

    def token_has_expired(self) -> bool:
        return pendulum.now() > self._token_expiry_date

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """Override to define additional parameters"""
        payload: MutableMapping[str, Any] = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.access_token_name], response_json[self.expires_in_name]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
