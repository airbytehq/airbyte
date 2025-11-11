#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta
from typing import Any, List, Mapping, Optional, Sequence, Tuple, Union

import dpath

from airbyte_cdk.config_observation import (
    create_connector_config_control_message,
    emit_configuration_as_airbyte_control_message,
)
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import (
    AbstractOauth2Authenticator,
)
from airbyte_cdk.utils.datetime_helpers import (
    AirbyteDateTime,
    ab_datetime_now,
    ab_datetime_parse,
)


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
        client_id_name: str = "client_id",
        client_secret_name: str = "client_secret",
        refresh_token_name: str = "refresh_token",
        scopes: List[str] | None = None,
        token_expiry_date: AirbyteDateTime | None = None,
        token_expiry_date_format: str | None = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_request_body: Mapping[str, Any] | None = None,
        refresh_request_headers: Mapping[str, Any] | None = None,
        grant_type_name: str = "grant_type",
        grant_type: str = "refresh_token",
        token_expiry_is_time_of_expiration: bool = False,
        refresh_token_error_status_codes: Tuple[int, ...] = (),
        refresh_token_error_key: str = "",
        refresh_token_error_values: Tuple[str, ...] = (),
    ) -> None:
        self._token_refresh_endpoint = token_refresh_endpoint
        self._client_secret_name = client_secret_name
        self._client_secret = client_secret
        self._client_id_name = client_id_name
        self._client_id = client_id
        self._refresh_token_name = refresh_token_name
        self._refresh_token = refresh_token
        self._scopes = scopes
        self._access_token_name = access_token_name
        self._expires_in_name = expires_in_name
        self._refresh_request_body = refresh_request_body
        self._refresh_request_headers = refresh_request_headers
        self._grant_type_name = grant_type_name
        self._grant_type = grant_type

        self._token_expiry_date = token_expiry_date or (ab_datetime_now() - timedelta(days=1))
        self._token_expiry_date_format = token_expiry_date_format
        self._token_expiry_is_time_of_expiration = token_expiry_is_time_of_expiration
        self._access_token = None
        super().__init__(
            refresh_token_error_status_codes, refresh_token_error_key, refresh_token_error_values
        )

    def get_token_refresh_endpoint(self) -> str:
        return self._token_refresh_endpoint

    def get_client_id_name(self) -> str:
        return self._client_id_name

    def get_client_id(self) -> str:
        return self._client_id

    def get_client_secret_name(self) -> str:
        return self._client_secret_name

    def get_client_secret(self) -> str:
        return self._client_secret

    def get_refresh_token_name(self) -> str:
        return self._refresh_token_name

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_access_token_name(self) -> str:
        return self._access_token_name

    def get_scopes(self) -> list[str]:
        return self._scopes  # type: ignore[return-value]

    def get_expires_in_name(self) -> str:
        return self._expires_in_name

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body  # type: ignore[return-value]

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        return self._refresh_request_headers  # type: ignore[return-value]

    def get_grant_type_name(self) -> str:
        return self._grant_type_name

    def get_grant_type(self) -> str:
        return self._grant_type

    def get_token_expiry_date(self) -> AirbyteDateTime:
        return self._token_expiry_date

    def set_token_expiry_date(self, value: AirbyteDateTime) -> None:
        self._token_expiry_date = value

    @property
    def token_expiry_is_time_of_expiration(self) -> bool:
        return self._token_expiry_is_time_of_expiration

    @property
    def token_expiry_date_format(self) -> Optional[str]:
        return self._token_expiry_date_format

    @property
    def access_token(self) -> str:
        return self._access_token  # type: ignore[return-value]

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = value  # type: ignore[assignment]  # Incorrect type for assignment


class SingleUseRefreshTokenOauth2Authenticator(Oauth2Authenticator):
    """
    Authenticator that should be used for API implementing single use refresh tokens:
    when refreshing access token some API returns a new refresh token that needs to used in the next refresh flow.
    This authenticator updates the configuration with new refresh token by emitting Airbyte control message from an observed mutation.
    By default, this authenticator expects a connector config with a "credentials" field with the following nested fields: client_id,
    client_secret, refresh_token. This behavior can be changed by defining custom config path (using dpath paths) in client_id_config_path,
    client_secret_config_path, refresh_token_config_path constructor arguments.
    """

    def __init__(
        self,
        connector_config: Mapping[str, Any],
        token_refresh_endpoint: str,
        scopes: List[str] | None = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_token_name: str = "refresh_token",
        refresh_request_body: Mapping[str, Any] | None = None,
        refresh_request_headers: Mapping[str, Any] | None = None,
        grant_type_name: str = "grant_type",
        grant_type: str = "refresh_token",
        client_id_name: str = "client_id",
        client_id: Optional[str] = None,
        client_secret_name: str = "client_secret",
        client_secret: Optional[str] = None,
        access_token_config_path: Sequence[str] = ("credentials", "access_token"),
        refresh_token_config_path: Sequence[str] = ("credentials", "refresh_token"),
        token_expiry_date_config_path: Sequence[str] = ("credentials", "token_expiry_date"),
        token_expiry_date_format: Optional[str] = None,
        message_repository: MessageRepository = NoopMessageRepository(),
        token_expiry_is_time_of_expiration: bool = False,
        refresh_token_error_status_codes: Tuple[int, ...] = (),
        refresh_token_error_key: str = "",
        refresh_token_error_values: Tuple[str, ...] = (),
    ) -> None:
        """
        Args:
            connector_config (Mapping[str, Any]): The full connector configuration
            token_refresh_endpoint (str): Full URL to the token refresh endpoint
            scopes (List[str], optional): List of OAuth scopes to pass in the refresh token request body. Defaults to None.
            access_token_name (str, optional): Name of the access token field, used to parse the refresh token response. Defaults to "access_token".
            expires_in_name (str, optional): Name of the name of the field that characterizes when the current access token will expire, used to parse the refresh token response. Defaults to "expires_in".
            refresh_token_name (str, optional): Name of the name of the refresh token field, used to parse the refresh token response. Defaults to "refresh_token".
            refresh_request_body (Mapping[str, Any], optional): Custom key value pair that will be added to the refresh token request body. Defaults to None.
            refresh_request_headers (Mapping[str, Any], optional): Custom key value pair that will be added to the refresh token request headers. Defaults to None.
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
        self._connector_config = connector_config
        self._client_id: str = self._get_config_value_by_path(
            ("credentials", "client_id"), client_id
        )
        self._client_secret: str = self._get_config_value_by_path(
            ("credentials", "client_secret"), client_secret
        )
        self._client_id_name = client_id_name
        self._client_secret_name = client_secret_name
        self._access_token_config_path = access_token_config_path
        self._refresh_token_config_path = refresh_token_config_path
        self._token_expiry_date_config_path = token_expiry_date_config_path
        self._token_expiry_date_format = token_expiry_date_format
        self._refresh_token_name = refresh_token_name
        self._grant_type_name = grant_type_name
        self._connector_config = connector_config
        self.__message_repository = message_repository
        super().__init__(
            token_refresh_endpoint=token_refresh_endpoint,
            client_id_name=self._client_id_name,
            client_id=self._client_id,
            client_secret_name=self._client_secret_name,
            client_secret=self._client_secret,
            refresh_token=self.get_refresh_token(),
            refresh_token_name=self._refresh_token_name,
            scopes=scopes,
            token_expiry_date=self.get_token_expiry_date(),
            access_token_name=access_token_name,
            expires_in_name=expires_in_name,
            refresh_request_body=refresh_request_body,
            refresh_request_headers=refresh_request_headers,
            grant_type_name=self._grant_type_name,
            grant_type=grant_type,
            token_expiry_date_format=token_expiry_date_format,
            token_expiry_is_time_of_expiration=token_expiry_is_time_of_expiration,
            refresh_token_error_status_codes=refresh_token_error_status_codes,
            refresh_token_error_key=refresh_token_error_key,
            refresh_token_error_values=refresh_token_error_values,
        )

    @property
    def access_token(self) -> str:
        """
        Retrieve the access token from the configuration.

        Returns:
            str: The access token.
        """
        return self._get_config_value_by_path(self._access_token_config_path)  # type: ignore[return-value]

    @access_token.setter
    def access_token(self, new_access_token: str) -> None:
        """
        Sets a new access token.

        Args:
            new_access_token (str): The new access token to be set.
        """
        self._set_config_value_by_path(self._access_token_config_path, new_access_token)

    def get_refresh_token(self) -> str:
        """
        Retrieve the refresh token from the configuration.

        This method fetches the refresh token using the configuration path specified
        by `_refresh_token_config_path`.

        Returns:
            str: The refresh token as a string.
        """
        return self._get_config_value_by_path(self._refresh_token_config_path)  # type: ignore[return-value]

    def set_refresh_token(self, new_refresh_token: str) -> None:
        """
        Updates the refresh token in the configuration.

        Args:
            new_refresh_token (str): The new refresh token to be set.
        """
        self._set_config_value_by_path(self._refresh_token_config_path, new_refresh_token)

    def get_token_expiry_date(self) -> AirbyteDateTime:
        """
        Retrieves the token expiry date from the configuration.

        This method fetches the token expiry date from the configuration using the specified path.
        If the expiry date is an empty string, it returns the current date and time minus one day.
        Otherwise, it parses the expiry date string into an AirbyteDateTime object.

        Returns:
            AirbyteDateTime: The parsed or calculated token expiry date.

        Raises:
            TypeError: If the result is not an instance of AirbyteDateTime.
        """
        expiry_date = self._get_config_value_by_path(self._token_expiry_date_config_path)
        result = (
            ab_datetime_now() - timedelta(days=1)
            if expiry_date == ""
            else ab_datetime_parse(str(expiry_date))
        )
        if isinstance(result, AirbyteDateTime):
            return result
        raise TypeError("Invalid datetime conversion")

    def set_token_expiry_date(self, new_token_expiry_date: AirbyteDateTime) -> None:  # type: ignore[override]
        """
        Sets the token expiry date in the configuration.

        Args:
            new_token_expiry_date (AirbyteDateTime): The new expiry date for the token.
        """
        self._set_config_value_by_path(
            self._token_expiry_date_config_path, str(new_token_expiry_date)
        )

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired"""
        return ab_datetime_now() > self.get_token_expiry_date()

    def get_access_token(self) -> str:
        """Retrieve new access and refresh token if the access token has expired.
        The new refresh token is persisted with the set_refresh_token function
        Returns:
            str: The current access_token, updated if it was previously expired.
        """
        if self.token_has_expired():
            new_access_token, access_token_expires_in, new_refresh_token = (
                self.refresh_access_token()
            )
            self.access_token = new_access_token
            self.set_refresh_token(new_refresh_token)
            self.set_token_expiry_date(access_token_expires_in)
            self._emit_control_message()
        return self.access_token

    def refresh_access_token(self) -> Tuple[str, AirbyteDateTime, str]:  # type: ignore[override]
        """
        Refreshes the access token by making a handled request and extracting the necessary token information.

        Returns:
            Tuple[str, str, str]: A tuple containing the new access token, token expiry date, and refresh token.
        """
        response_json = self._make_handled_request()
        return (
            self._extract_access_token(response_json),
            self._extract_token_expiry_date(response_json),
            self._extract_refresh_token(response_json),
        )

    def _set_config_value_by_path(self, config_path: Union[str, Sequence[str]], value: Any) -> None:
        """
        Set a value in the connector configuration at the specified path.

        Args:
            config_path (Union[str, Sequence[str]]): The path within the configuration where the value should be set.
                This can be a string representing a single key or a sequence of strings representing a nested path.
            value (Any): The value to set at the specified path in the configuration.

        Returns:
            None
        """
        dpath.new(self._connector_config, config_path, value)  # type: ignore[arg-type]

    def _get_config_value_by_path(
        self, config_path: Union[str, Sequence[str]], default: Optional[str] = None
    ) -> str | Any:
        """
        Retrieve a value from the connector configuration using a specified path.

        Args:
            config_path (Union[str, Sequence[str]]): The path to the desired configuration value. This can be a string or a sequence of strings.
            default (Optional[str], optional): The default value to return if the specified path does not exist in the configuration. Defaults to None.

        Returns:
            Any: The value from the configuration at the specified path, or the default value if the path does not exist.
        """
        return dpath.get(
            self._connector_config,  # type: ignore[arg-type]
            config_path,
            default=default if default is not None else "",
        )

    def _emit_control_message(self) -> None:
        """
        Emits a control message based on the connector configuration.

        This method checks if the message repository is not a NoopMessageRepository.
        If it is not, it emits a message using the message repository. Otherwise,
        it falls back to emitting the configuration as an Airbyte control message
        directly to the console for backward compatibility.

        Note:
            The function `emit_configuration_as_airbyte_control_message` has been deprecated
            in favor of the package `airbyte_cdk.sources.message`.

        Raises:
            TypeError: If the argument types are incorrect.
        """
        # FIXME emit_configuration_as_airbyte_control_message as been deprecated in favor of package airbyte_cdk.sources.message
        # Usually, a class shouldn't care about the implementation details but to keep backward compatibility where we print the
        # message directly in the console, this is needed
        if not isinstance(self._message_repository, NoopMessageRepository):
            self._message_repository.emit_message(
                create_connector_config_control_message(self._connector_config)  # type: ignore[arg-type]
            )
        else:
            emit_configuration_as_airbyte_control_message(self._connector_config)  # type: ignore[arg-type]

    @property
    def _message_repository(self) -> MessageRepository:
        """
        Overriding AbstractOauth2Authenticator._message_repository to allow for HTTP request logs
        """
        return self.__message_repository
