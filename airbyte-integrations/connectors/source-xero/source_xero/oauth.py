#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, List, Mapping, MutableMapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

logger = logging.getLogger("airbyte")


class XeroCustomConnectionsOauth2Authenticator(Oauth2Authenticator):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.
    """

    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        scopes: List[str] = None,
        token_expiry_date: pendulum.DateTime = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
    ):
        self.token_refresh_endpoint = token_refresh_endpoint
        self.client_secret = client_secret
        self.client_id = client_id
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

    def token_has_expired(self) -> bool:
        return pendulum.now() > self._token_expiry_date

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        return payload

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        headers: MutableMapping[str, Any] = {
            "Authorization": "Basic " + str(base64.b64encode(bytes(self.client_id + ":" + self.client_secret, "utf-8")), "utf-8")
        }

        return headers

    def refresh_access_token(self) -> Tuple[str, int]:
        response = requests.request(
            method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body(), headers=self.get_refresh_request_headers()
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json[self.access_token_name], response_json[self.expires_in_name]
