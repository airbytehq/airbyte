#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pendulum
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator


class Oauth2Authenticator(AbstractOauth2Authenticator):
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
        token_expiry_date: pendulum.DateTime = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_request_body: Mapping[str, Any] = None,
    ):
        self.token_refresh_endpoint = token_refresh_endpoint
        self.client_secret = client_secret
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.scopes = scopes
        self.access_token_name = access_token_name
        self.expires_in_name = expires_in_name
        self.refresh_request_body = refresh_request_body

        self.token_expiry_date = token_expiry_date or pendulum.now().subtract(days=1)
        self.access_token = None

    @property
    def token_refresh_endpoint(self) -> str:
        return self._token_refresh_endpoint

    @token_refresh_endpoint.setter
    def token_refresh_endpoint(self, value: str):
        self._token_refresh_endpoint = value

    @property
    def client_id(self) -> str:
        return self._client_id

    @client_id.setter
    def client_id(self, value: str):
        self._client_id = value

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value: str):
        self._client_secret = value

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str):
        self._refresh_token = value

    @property
    def access_token_name(self) -> str:
        return self._access_token_name

    @access_token_name.setter
    def access_token_name(self, value: str):
        self._access_token_name = value

    @property
    def scopes(self) -> [str]:
        return self._scopes

    @scopes.setter
    def scopes(self, value: [str]):
        self._scopes = value

    @property
    def token_expiry_date(self) -> pendulum.DateTime:
        return self._token_expiry_date

    @token_expiry_date.setter
    def token_expiry_date(self, value: pendulum.DateTime):
        self._token_expiry_date = value

    @property
    def expires_in_name(self) -> str:
        return self._expires_in_name

    @expires_in_name.setter
    def expires_in_name(self, value):
        self._expires_in_name = value

    @property
    def refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body

    @refresh_request_body.setter
    def refresh_request_body(self, value: Mapping[str, Any]):
        self._refresh_request_body = value

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value
