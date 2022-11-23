#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.config_observation import observe_connector_config
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


class SingleUseRefreshTokenOauth2Authenticator(Oauth2Authenticator):
    def __init__(
        self,
        connector_config: Mapping[str, Any],
        token_refresh_endpoint: str,
        scopes: List[str] = None,
        token_expiry_date: pendulum.DateTime = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_token_name: str = "refresh_token",
        refresh_request_body: Mapping[str, Any] = None,
        grant_type: str = "refresh_token",
        credentials_configuration_field_name: str = "credentials",
    ):
        self.credentials_configuration_field_name = credentials_configuration_field_name
        self._refresh_token_name = refresh_token_name
        self._connector_config = observe_connector_config(connector_config)
        self._validate_config()
        super().__init__(
            token_refresh_endpoint,
            self.get_client_id(),
            self.get_client_secret(),
            self.get_refresh_token(),
            scopes,
            token_expiry_date,
            access_token_name,
            expires_in_name,
            refresh_request_body,
            grant_type,
        )

    def _validate_config(self):
        for field_name, getter in [
            ("client_id", self.get_client_id),
            ("client_secret", self.get_client_secret),
            (self.get_refresh_token_name(), self.get_refresh_token),
        ]:
            try:
                getter()
            except KeyError:
                raise ValueError(
                    f"This authenticator expects a {field_name} field under the {self.credentials_configuration_field_name} field. Please override this class getters or change your configuration structure."
                )

    def get_refresh_token_name(self) -> str:
        return self._refresh_token_name

    def _get_config_credentials_field(self, field_name):
        return self._connector_config[self.credentials_configuration_field_name][field_name]

    def get_client_id(self) -> str:
        return self._get_config_credentials_field("client_id")

    def get_client_secret(self) -> str:
        return self._get_config_credentials_field("client_secret")

    def set_refresh_token(self, new_refresh_token: str):
        self._connector_config[self.credentials_configuration_field_name][self.get_refresh_token_name()] = new_refresh_token

    def get_refresh_token(self) -> str:
        return self._get_config_credentials_field(self.get_refresh_token_name())

    def get_access_token(self) -> str:
        """Returns the access token"""
        if self.token_has_expired():
            t0 = pendulum.now()
            new_access_token, access_token_expires_in, new_refresh_token = self.refresh_access_token()
            self.access_token = new_access_token
            self.set_token_expiry_date(t0.add(seconds=access_token_expires_in))
            self.set_refresh_token(new_refresh_token)
        return self.access_token

    def refresh_access_token(self) -> Tuple[str, int, str]:
        try:
            response_json = self._get_refresh_access_token_response()
            return (
                response_json[self.get_access_token_name()],
                response_json[self.get_expires_in_name()],
                response_json[self.get_refresh_token_name()],
            )
        except Exception as e:
            raise Exception(f"Error while refreshing access token and refresh token: {e}") from e
