#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Sequence, Tuple, Union

import dpath
import pendulum
from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
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
        token_expiry_date_format: str = None,
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
        self._token_expiry_date_format = token_expiry_date_format
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

    def set_token_expiry_date(self, initial_time: pendulum.DateTime, value: Union[str, int]):
        if self._token_expiry_date_format:
            self._token_expiry_date = pendulum.from_format(value, self._token_expiry_date_format)
        else:
            self._token_expiry_date = initial_time.add(seconds=value)

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value


class SingleUseRefreshTokenOauth2Authenticator(Oauth2Authenticator):
    """
    Authenticator that should be used for API implementing single use refresh tokens:
    when refreshing access token some API returns a new refresh token that needs to used in the next refresh flow.
    This authenticator updates the configuration with new refresh token by emitting Airbyte control message from an observed mutation.
    By default this authenticator expects a connector config with a"credentials" field with the following nested fields: client_id, client_secret, refresh_token.
    This behavior can be changed by defining custom config path (using dpath paths) in client_id_config_path, client_secret_config_path, refresh_token_config_path constructor arguments.
    """

    def __init__(
        self,
        connector_config: Mapping[str, Any],
        token_refresh_endpoint: str,
        scopes: List[str] = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_token_name: str = "refresh_token",
        refresh_request_body: Mapping[str, Any] = None,
        grant_type: str = "refresh_token",
        client_id_config_path: Sequence[str] = ("credentials", "client_id"),
        client_secret_config_path: Sequence[str] = ("credentials", "client_secret"),
        access_token_config_path: Sequence[str] = ("credentials", "access_token"),
        refresh_token_config_path: Sequence[str] = ("credentials", "refresh_token"),
        access_token_expiration_datetime_config_path: Sequence[str] = ("credentials", "access_token_expiration_datetime"),
    ):
        """

        Args:
            connector_config (Mapping[str, Any]): The full connector configuration
            token_refresh_endpoint (str): Full URL to the token refresh endpoint
            scopes (List[str], optional): List of OAuth scopes to pass in the refresh token request body. Defaults to None.
            access_token_name (str, optional): Name of the access token field, used to parse the refresh token response. Defaults to "access_token".
            expires_in_name (str, optional): Name of the name of the field that characterizes when the current access token will expire, used to parse the refresh token response. Defaults to "expires_in".
            refresh_token_name (str, optional): Name of the name of the refresh token field, used to parse the refresh token response. Defaults to "refresh_token".
            refresh_request_body (Mapping[str, Any], optional): Custom key value pair that will be added to the refresh token request body. Defaults to None.
            grant_type (str, optional): OAuth grant type. Defaults to "refresh_token".
            client_id_config_path (Sequence[str]): Dpath to the client_id field in the connector configuration. Defaults to ("credentials", "client_id").
            client_secret_config_path (Sequence[str]): Dpath to the client_secret field in the connector configuration. Defaults to ("credentials", "client_secret").
            access_token_config_path (Sequence[str]): Dpath to the access_token field in the connector configuration. Defaults to ("credentials", "access_token").
            refresh_token_config_path (Sequence[str]): Dpath to the refresh_token field in the connector configuration. Defaults to ("credentials", "refresh_token").
            access_token_expiration_datetime_config_path (Sequence[str]): Dpath to the access_token_expiration_datetime field in the connector configuration. Defaults to ("credentials", "access_token_expiration_datetime").
        """
        self._client_id_config_path = client_id_config_path
        self._client_secret_config_path = client_secret_config_path
        self._access_token_config_path = access_token_config_path
        self._refresh_token_config_path = refresh_token_config_path
        self._access_token_expiration_datetime_config_path = access_token_expiration_datetime_config_path
        self._refresh_token_name = refresh_token_name
        self._connector_config = connector_config
        self._validate_connector_config()
        super().__init__(
            token_refresh_endpoint,
            self.get_client_id(),
            self.get_client_secret(),
            self.get_refresh_token(),
            scopes=scopes,
            token_expiry_date=self.get_access_token_expiration_datetime(),
            access_token_name=access_token_name,
            expires_in_name=expires_in_name,
            refresh_request_body=refresh_request_body,
            grant_type=grant_type
        )

    def _validate_connector_config(self):
        """Validates the defined getters for configuration values are returning values.

        Raises:
            ValueError: Raised if the defined getters are not returning a value.
        """
        for field_path, getter, parameter_name in [
            (self._client_id_config_path, self.get_client_id, "client_id_config_path"),
            (self._client_secret_config_path, self.get_client_secret, "client_secret_config_path"),
            (self._refresh_token_config_path, self.get_refresh_token, "refresh_token_config_path"),
            (self._access_token_expiration_datetime_config_path, self.get_access_token_expiration_datetime, "access_token_expiration_datetime_config_path"),
        ]:
            try:
                assert getter()
            except KeyError:
                raise ValueError(
                    f"This authenticator expects a value under the {field_path} field path. Please check your configuration structure or change the {parameter_name} value at initialization of this authenticator."
                )

    def get_refresh_token_name(self) -> str:
        return self._refresh_token_name

    def get_client_id(self) -> str:
        return dpath.util.get(self._connector_config, self._client_id_config_path)

    def get_client_secret(self) -> str:
        return dpath.util.get(self._connector_config, self._client_secret_config_path)

    def get_refresh_token(self) -> str:
        return dpath.util.get(self._connector_config, self._refresh_token_config_path)

    def get_access_token_expiration_datetime(self) -> pendulum.DateTime:
        return pendulum.parse(dpath.util.get(self._connector_config, self._access_token_expiration_datetime_config_path))


    def _update_config_with_access_and_refresh_tokens(self, new_access_token: str, new_refresh_token: str, new_access_token_expiration_datetime: pendulum.DateTime):
        """Update the connector configuration with new access and refresh token values. 
        The mutation of the connector_config object will emit Airbyte control messages.

        Args:
            new_access_token (str): The new access token value.
            new_refresh_token (str): The new refresh token value.
            new_access_token_expiration_datetime (pendulum.DateTime): The new access token expiration date.
        """
        dpath.util.set(self._connector_config, self._access_token_config_path, new_access_token)
        dpath.util.set(self._connector_config, self._refresh_token_config_path, new_refresh_token)
        dpath.util.set(self._connector_config, self._access_token_expiration_datetime_config_path, new_access_token_expiration_datetime)
        emit_configuration_as_airbyte_control_message(self._connector_config)

    def get_access_token(self) -> str:
        """Retrieve new access and refresh token if the access token has expired.
        The new refresh token is persisted with the set_refresh_token function
        Returns:
            str: The current access_token, updated if it was previously expired.
        """
        if self.token_has_expired():
            new_access_token, access_token_expires_in, new_refresh_token = self.refresh_access_token()
            self.access_token = new_access_token
            self.set_token_expiry_date(pendulum.now("UTC"), access_token_expires_in)
            self._update_config_with_access_and_refresh_tokens(new_access_token, new_refresh_token, self.get_token_expiry_date())
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

