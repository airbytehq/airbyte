#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Sequence, Tuple, Union

import dpath
import pendulum
from airbyte_cdk.config_observation import create_connector_config_control_message, emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
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
        token_expiry_is_time_of_expiration: bool = False,
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
        self._token_expiry_is_time_of_expiration = token_expiry_is_time_of_expiration
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

    def set_token_expiry_date(self, value: Union[str, int]):
        self._token_expiry_date = self._parse_token_expiration_date(value)

    @property
    def token_expiry_is_time_of_expiration(self) -> bool:
        return self._token_expiry_is_time_of_expiration

    @property
    def token_expiry_date_format(self) -> Optional[str]:
        return self._token_expiry_date_format

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
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token_config_path: Sequence[str] = ("credentials", "access_token"),
        refresh_token_config_path: Sequence[str] = ("credentials", "refresh_token"),
        token_expiry_date_config_path: Sequence[str] = ("credentials", "token_expiry_date"),
        token_expiry_date_format: Optional[str] = None,
        message_repository: MessageRepository = NoopMessageRepository(),
        token_expiry_is_time_of_expiration: bool = False,
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
            client_id (Optional[str]): The client id to authenticate. If not specified, defaults to credentials.client_id in the config object.
            client_secret (Optional[str]): The client secret to authenticate. If not specified, defaults to credentials.client_secret in the config object.
            access_token_config_path (Sequence[str]): Dpath to the access_token field in the connector configuration. Defaults to ("credentials", "access_token").
            refresh_token_config_path (Sequence[str]): Dpath to the refresh_token field in the connector configuration. Defaults to ("credentials", "refresh_token").
            token_expiry_date_config_path (Sequence[str]): Dpath to the token_expiry_date field in the connector configuration. Defaults to ("credentials", "token_expiry_date").
            token_expiry_date_format (Optional[str]): Date format of the token expiry date field (set by expires_in_name). If not specified the token expiry date is interpreted as number of seconds until expiration.
            token_expiry_is_time_of_expiration bool: set True it if expires_in is returned as time of expiration instead of the number seconds until expiration
            message_repository (MessageRepository): the message repository used to emit logs on HTTP requests and control message on config update
        """
        self._client_id = client_id if client_id is not None else dpath.util.get(connector_config, ("credentials", "client_id"))
        self._client_secret = (
            client_secret if client_secret is not None else dpath.util.get(connector_config, ("credentials", "client_secret"))
        )
        self._access_token_config_path = access_token_config_path
        self._refresh_token_config_path = refresh_token_config_path
        self._token_expiry_date_config_path = token_expiry_date_config_path
        self._token_expiry_date_format = token_expiry_date_format
        self._refresh_token_name = refresh_token_name
        self._connector_config = connector_config
        self.__message_repository = message_repository
        super().__init__(
            token_refresh_endpoint,
            self.get_client_id(),
            self.get_client_secret(),
            self.get_refresh_token(),
            scopes=scopes,
            token_expiry_date=self.get_token_expiry_date(),
            access_token_name=access_token_name,
            expires_in_name=expires_in_name,
            refresh_request_body=refresh_request_body,
            grant_type=grant_type,
            token_expiry_date_format=token_expiry_date_format,
            token_expiry_is_time_of_expiration=token_expiry_is_time_of_expiration,
        )

    def get_refresh_token_name(self) -> str:
        return self._refresh_token_name

    def get_client_id(self) -> str:
        return self._client_id

    def get_client_secret(self) -> str:
        return self._client_secret

    @property
    def access_token(self) -> str:
        return dpath.util.get(self._connector_config, self._access_token_config_path, default="")

    @access_token.setter
    def access_token(self, new_access_token: str):
        dpath.util.new(self._connector_config, self._access_token_config_path, new_access_token)

    def get_refresh_token(self) -> str:
        return dpath.util.get(self._connector_config, self._refresh_token_config_path, default="")

    def set_refresh_token(self, new_refresh_token: str):
        dpath.util.new(self._connector_config, self._refresh_token_config_path, new_refresh_token)

    def get_token_expiry_date(self) -> pendulum.DateTime:
        expiry_date = dpath.util.get(self._connector_config, self._token_expiry_date_config_path, default="")
        return pendulum.now().subtract(days=1) if expiry_date == "" else pendulum.parse(expiry_date)

    def set_token_expiry_date(self, new_token_expiry_date):
        dpath.util.new(self._connector_config, self._token_expiry_date_config_path, str(new_token_expiry_date))

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired"""
        return pendulum.now("UTC") > self.get_token_expiry_date()

    @staticmethod
    def get_new_token_expiry_date(access_token_expires_in: str, token_expiry_date_format: str = None) -> pendulum.DateTime:
        if token_expiry_date_format:
            return pendulum.from_format(access_token_expires_in, token_expiry_date_format)
        else:
            return pendulum.now("UTC").add(seconds=int(access_token_expires_in))

    def get_access_token(self) -> str:
        """Retrieve new access and refresh token if the access token has expired.
        The new refresh token is persisted with the set_refresh_token function
        Returns:
            str: The current access_token, updated if it was previously expired.
        """
        if self.token_has_expired():
            new_access_token, access_token_expires_in, new_refresh_token = self.refresh_access_token()
            new_token_expiry_date = self.get_new_token_expiry_date(access_token_expires_in, self._token_expiry_date_format)
            self.access_token = new_access_token
            self.set_refresh_token(new_refresh_token)
            self.set_token_expiry_date(new_token_expiry_date)
            # FIXME emit_configuration_as_airbyte_control_message as been deprecated in favor of package airbyte_cdk.sources.message
            #  Usually, a class shouldn't care about the implementation details but to keep backward compatibility where we print the
            #  message directly in the console, this is needed
            if not isinstance(self._message_repository, NoopMessageRepository):
                self._message_repository.emit_message(create_connector_config_control_message(self._connector_config))
            else:
                emit_configuration_as_airbyte_control_message(self._connector_config)
        return self.access_token

    def refresh_access_token(self) -> Tuple[str, str, str]:
        response_json = self._get_refresh_access_token_response()
        return (
            response_json[self.get_access_token_name()],
            response_json[self.get_expires_in_name()],
            response_json[self.get_refresh_token_name()],
        )

    @property
    def _message_repository(self) -> MessageRepository:
        """
        Overriding AbstractOauth2Authenticator._message_repository to allow for HTTP request logs
        """
        return self.__message_repository
