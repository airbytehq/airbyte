#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping

import pendulum
from airbyte_cdk.config_observation import ConfigObserver, ObservedDict
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator


class Oauth2Authenticator(AbstractOauth2Authenticator):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.
    If a connector_config is provided any mutation of it's value in the scope of this class will emit AirbyteControlConnectorConfigMessage.
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
        grant_type: str = "refresh_token",
        connector_config: Mapping[str, Any] = None,
    ):
        self._token_refresh_endpoint = token_refresh_endpoint
        self._client_secret = client_secret
        self._client_id = client_id
        self._refresh_token = refresh_token
        self._scopes = scopes
        self._access_token_name = access_token_name
        self._expires_in_name = expires_in_name
        self._refresh_request_body = refresh_request_body
        self._grant_type = grant_type

        self._token_expiry_date = token_expiry_date or pendulum.now().subtract(days=1)
        self._access_token = None
        self._connector_config = self._observe_connector_config(connector_config) if connector_config else None

    def _observe_connector_config(self, non_observed_connector_config: MutableMapping):
        if isinstance(non_observed_connector_config, ObservedDict):
            raise ValueError("This connector configuration is already observed")
        connector_config_observer = ConfigObserver()
        observed_connector_config = ObservedDict(non_observed_connector_config, connector_config_observer)
        connector_config_observer.set_config(observed_connector_config)
        return observed_connector_config

    def get_token_refresh_endpoint(self) -> str:
        return self._token_refresh_endpoint

    def get_client_id(self) -> str:
        return self._client_id

    def get_client_secret(self) -> str:
        return self._client_secret

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_access_token_name(self) -> str:
        return self._access_token_name

    def get_scopes(self) -> [str]:
        return self._scopes

    def get_expires_in_name(self) -> str:
        return self._expires_in_name

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body

    def get_grant_type(self) -> str:
        return self._grant_type

    def get_token_expiry_date(self) -> pendulum.DateTime:
        return self._token_expiry_date

    def set_token_expiry_date(self, value: pendulum.DateTime):
        self._token_expiry_date = value

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value
