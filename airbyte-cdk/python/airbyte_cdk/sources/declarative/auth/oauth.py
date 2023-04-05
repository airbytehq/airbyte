#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional, Sequence, Tuple, Union

import dpath
import pendulum
from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator


@dataclass
class DeclarativeOauth2Authenticator(AbstractOauth2Authenticator, DeclarativeAuthenticator):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials based on
    a declarative connector configuration file. Credentials can be defined explicitly or via interpolation
    at runtime. The generated access token is attached to each request via the Authorization header.

    Attributes:
        token_refresh_endpoint (Union[InterpolatedString, str]): The endpoint to refresh the access token
        client_id (Union[InterpolatedString, str]): The client id
        client_secret (Union[InterpolatedString, str]): Client secret
        refresh_token (Union[InterpolatedString, str]): The token used to refresh the access token
        access_token_name (Union[InterpolatedString, str]): THe field to extract access token from in the response
        expires_in_name (Union[InterpolatedString, str]): The field to extract expires_in from in the response
        config (Mapping[str, Any]): The user-provided configuration as specified by the source's spec
        scopes (Optional[List[str]]): The scopes to request
        token_expiry_date (Optional[Union[InterpolatedString, str]]): The access token expiration date
        token_expiry_date_format str: format of the datetime; provide it if expires_in is returned in datetime instead of seconds
        refresh_request_body (Optional[Mapping[str, Any]]): The request body to send in the refresh request
        grant_type: The grant_type to request for access_token
    """

    token_refresh_endpoint: Union[InterpolatedString, str]
    client_id: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    refresh_token: Union[InterpolatedString, str]
    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    scopes: Optional[List[str]] = None
    token_expiry_date: Optional[Union[InterpolatedString, str]] = None
    _token_expiry_date: pendulum.DateTime = field(init=False, repr=False, default=None)
    token_expiry_date_format: str = None
    access_token_name: Union[InterpolatedString, str] = "access_token"
    expires_in_name: Union[InterpolatedString, str] = "expires_in"
    refresh_request_body: Optional[Mapping[str, Any]] = None
    grant_type: Union[InterpolatedString, str] = "refresh_token"

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.token_refresh_endpoint = InterpolatedString.create(self.token_refresh_endpoint, parameters=parameters)
        self.client_id = InterpolatedString.create(self.client_id, parameters=parameters)
        self.client_secret = InterpolatedString.create(self.client_secret, parameters=parameters)
        self.refresh_token = InterpolatedString.create(self.refresh_token, parameters=parameters)
        self.access_token_name = InterpolatedString.create(self.access_token_name, parameters=parameters)
        self.expires_in_name = InterpolatedString.create(self.expires_in_name, parameters=parameters)
        self.grant_type = InterpolatedString.create(self.grant_type, parameters=parameters)
        self._refresh_request_body = InterpolatedMapping(self.refresh_request_body or {}, parameters=parameters)
        self._token_expiry_date = (
            pendulum.parse(InterpolatedString.create(self.token_expiry_date, parameters=parameters).eval(self.config))
            if self.token_expiry_date
            else pendulum.now().subtract(days=1)
        )
        self._access_token = None

    def get_token_refresh_endpoint(self) -> str:
        return self.token_refresh_endpoint.eval(self.config)

    def get_client_id(self) -> str:
        return self.client_id.eval(self.config)

    def get_client_secret(self) -> str:
        return self.client_secret.eval(self.config)

    def get_refresh_token(self) -> str:
        return self.refresh_token.eval(self.config)

    def get_scopes(self) -> [str]:
        return self.scopes

    def get_access_token_name(self) -> InterpolatedString:
        return self.access_token_name.eval(self.config)

    def get_expires_in_name(self) -> InterpolatedString:
        return self.expires_in_name.eval(self.config)

    def get_grant_type(self) -> InterpolatedString:
        return self.grant_type.eval(self.config)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body.eval(self.config)

    def refresh_access_token(self) -> Tuple[str, Any]:
        """
        This overrides the parent class method because the parent class assumes the "expires_in" field is always an int representing
         seconds till token expiry.

        However, this class provides the ability to determine the expiry date of an access token either by using (pseudocode):
        * expiry_datetime = datetime.now() + seconds_till_access_token_expiry # in this option we have to calculate expiry timestamp, OR
        * expiry_datetime = parse(response.body["expires_at"]) # in this option the API tells us exactly when access token expires

        :return: a tuple of (access_token, either token_lifespan_in_seconds or datetime_of_token_expiry)

        # TODO this is a hack and should be better encapsulated/enabled by the AbstractOAuthAuthenticator i.e: that class should have
                a method which takes the HTTP response and returns a timestamp for when the access token will expire which subclasses
                such as this one can override or just configure directly.
        """
        response_json = self._get_refresh_access_token_response()
        return response_json[self.get_access_token_name()], response_json[self.get_expires_in_name()]

    def get_token_expiry_date(self) -> pendulum.DateTime:
        return self._token_expiry_date

    def set_token_expiry_date(self, value: Union[str, int]):
        if self.token_expiry_date_format:
            self._token_expiry_date = pendulum.from_format(value, self.token_expiry_date_format)
        else:
            self._token_expiry_date = pendulum.now().add(seconds=value)

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value


@dataclass
class DeclarativeSingleUseRefreshTokenOauth2Authenticator(AbstractOauth2Authenticator, DeclarativeAuthenticator):
    """
    Authenticator that should be used for API implementing single use refresh tokens based on a declarative connector configuration file:
    hen refreshing access token some API returns a new refresh token that needs to be used in the next refresh flow.
    This authenticator updates the configuration with new refresh token by emitting Airbyte control message from an observed mutation.
    By default, this authenticator expects a connector config with a "credentials" field with the following nested fields:
    client_id, client_secret, refresh_token, access_token, token_expiry_date.

    Attributes:
        token_refresh_endpoint (Union[InterpolatedString, str]): Full URL to the token refresh endpoint
        config (Mapping[str, Any]): The user-provided configuration as specified by the source's spec
        scopes (Optional[List[str]]): List of OAuth scopes to pass in the refresh token request body. Defaults to None.
        access_token_name (Union[InterpolatedString, str]): The field to extract access token from in the response. Defaults to "access_token".
        refresh_token_name (Union[InterpolatedString, str]): The field to extract refresh token from in the response. Defaults to "refresh_token".
        expires_in_name (Union[InterpolatedString, str]): The field to extract expires_in from in the response. Defaults to "expires_in".
        refresh_request_body (Optional[Mapping[str, Any]]): The request body to send in the refresh request. Defaults to None.
        grant_type: OAuth grant type. Defaults to "refresh_token".
        client_id_config_path (Sequence[str]): Dpath to the client_id field in the connector configuration. Defaults to ("credentials", "client_id").
        client_secret_config_path (Sequence[str]): Dpath to the client_secret field in the connector configuration. Defaults to ("credentials", "client_secret").
        access_token_config_path (Sequence[str]): Dpath to the access_token field in the connector configuration. Defaults to ("credentials", "access_token").
        refresh_token_config_path (Sequence[str]): Dpath to the refresh_token field in the connector configuration. Defaults to ("credentials", "refresh_token").
        token_expiry_date_config_path (Sequence[str]): Dpath to the token_expiry_date field in the connector configuration. Defaults to ("credentials", "token_expiry_date").
    """

    config: Mapping[str, Any]
    token_refresh_endpoint: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    scopes: Optional[List[str]] = None
    access_token_name: Union[InterpolatedString, str] = "access_token"
    refresh_token_name: Union[InterpolatedString, str] = "refresh_token"
    expires_in_name: Union[InterpolatedString, str] = "expires_in"
    refresh_request_body: Optional[Mapping[str, Any]] = None
    grant_type: Union[InterpolatedString, str] = "refresh_token"
    client_id_config_path: InitVar[Optional[Sequence[str]]] = ("credentials", "client_id")
    client_secret_config_path: InitVar[Optional[Sequence[str]]] = ("credentials", "client_secret")
    access_token_config_path: InitVar[Optional[Sequence[str]]] = ("credentials", "access_token")
    refresh_token_config_path: InitVar[Optional[Sequence[str]]] = ("credentials", "refresh_token")
    token_expiry_date_config_path: InitVar[Optional[Sequence[str]]] = ("credentials", "token_expiry_date")

    def __post_init__(
        self,
        parameters: Mapping[str, Any],
        client_id_config_path: Sequence[str],
        client_secret_config_path: Sequence[str],
        access_token_config_path: Sequence[str],
        refresh_token_config_path: Sequence[str],
        token_expiry_date_config_path: Sequence[str],
    ):
        self._client_id_config_path = client_id_config_path
        self._client_secret_config_path = client_secret_config_path
        self._access_token_config_path = access_token_config_path
        self._refresh_token_config_path = refresh_token_config_path
        self._token_expiry_date_config_path = token_expiry_date_config_path
        self._validate_connector_config()
        self.token_refresh_endpoint = InterpolatedString.create(self.token_refresh_endpoint, parameters=parameters)
        self.access_token_name = InterpolatedString.create(self.access_token_name, parameters=parameters)
        self.refresh_token_name = InterpolatedString.create(self.refresh_token_name, parameters=parameters)
        self.expires_in_name = InterpolatedString.create(self.expires_in_name, parameters=parameters)
        self.grant_type = InterpolatedString.create(self.grant_type, parameters=parameters)

    def _validate_connector_config(self):
        """Validates the defined getters for configuration values are returning values.

        Raises:
            ValueError: Raised if the defined getters are not returning a value.
        """
        try:
            assert self.access_token
        except KeyError:
            raise ValueError(
                f"This authenticator expects a value under the {self._access_token_config_path} field path. Please check your configuration structure or change the access_token_config_path value at initialization of this authenticator."
            )
        for field_path, getter, parameter_name in [
            (self._client_id_config_path, self.get_client_id, "client_id_config_path"),
            (self._client_secret_config_path, self.get_client_secret, "client_secret_config_path"),
            (self._refresh_token_config_path, self.get_refresh_token, "refresh_token_config_path"),
            (self._token_expiry_date_config_path, self.get_token_expiry_date, "token_expiry_date_config_path"),
        ]:
            try:
                assert getter()
            except KeyError:
                raise ValueError(
                    f"This authenticator expects a value under the {field_path} field path. Please check your configuration structure or change the {parameter_name} value at initialization of this authenticator."
                )

    def get_client_id(self) -> str:
        return dpath.util.get(self.config, self._client_id_config_path)

    def get_client_secret(self) -> str:
        return dpath.util.get(self.config, self._client_secret_config_path)

    @property
    def access_token(self) -> str:
        return dpath.util.get(self.config, self._access_token_config_path)

    @access_token.setter
    def access_token(self, value: str):
        dpath.util.set(self.config, self._access_token_config_path, value)

    def get_token_refresh_endpoint(self) -> str:
        return self.token_refresh_endpoint.eval(self.config)

    def get_token_expiry_date(self) -> pendulum.DateTime:
        return pendulum.parse(dpath.util.get(self.config, self._token_expiry_date_config_path))

    def set_token_expiry_date(self, value: Union[str, int]):
        if isinstance(value, int):
            expiry_date = pendulum.now("UTC").add(seconds=value)
        elif value.isdigit():
            expiry_date = pendulum.now("UTC").add(seconds=int(value))
        else:
            expiry_date = pendulum.parse(value)
        dpath.util.set(self.config, self._token_expiry_date_config_path, str(expiry_date))

    def set_refresh_token(self, new_refresh_token: str):
        dpath.util.set(self.config, self._refresh_token_config_path, new_refresh_token)

    def get_refresh_token(self) -> str:
        return dpath.util.get(self.config, self._refresh_token_config_path)

    def get_scopes(self) -> List[str]:
        return self.scopes

    def get_access_token_name(self) -> str:
        return self.access_token_name.eval(self.config)

    def get_refresh_token_name(self) -> str:
        return self.refresh_token_name.eval(self.config)

    def get_expires_in_name(self) -> str:
        return self.expires_in_name.eval(self.config)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self.refresh_request_body

    def get_grant_type(self) -> str:
        return self.grant_type.eval(self.config)

    def get_access_token(self) -> str:
        """
        Retrieve new access and refresh token if the access token has expired.
        The new refresh token is persisted with the set_refresh_token function
        Returns:
            str: The current access_token, updated if it was previously expired.
        """
        if self.token_has_expired():
            new_access_token, access_token_expires_in, new_refresh_token = self.refresh_access_token()
            self.access_token = new_access_token
            self.set_refresh_token(new_refresh_token)
            self.set_token_expiry_date(access_token_expires_in)
            emit_configuration_as_airbyte_control_message(self.config)
        return self.access_token

    def refresh_access_token(self) -> Tuple[str, Union[int, str], str]:
        response_json = self._get_refresh_access_token_response()
        return (
            response_json[self.get_access_token_name()],
            response_json[self.get_expires_in_name()],
            response_json[self.get_refresh_token_name()],
        )
