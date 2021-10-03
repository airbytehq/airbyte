#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Tuple

import pendulum
import requests
from deprecated import deprecated

from .core import HttpAuthenticator


@deprecated(version="0.1.20", reason="Use airbyte_cdk.sources.streams.http.requests_native_auth.Oauth2Authenticator instead")
class Oauth2Authenticator(HttpAuthenticator):
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
        refresh_access_token_headers: Mapping[str, Any] = None,
    ):
        self.token_refresh_endpoint = token_refresh_endpoint
        self.client_secret = client_secret
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.scopes = scopes
        self.refresh_access_token_headers = refresh_access_token_headers

        self._token_expiry_date = pendulum.now().subtract(days=1)
        self._access_token = None

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
        """ Override to define additional parameters """
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
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                headers=self.refresh_access_token_headers,
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
