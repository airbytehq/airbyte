#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional, Union

import pendulum
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator


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
        token_expiry_is_time_of_expiration bool: set True it if expires_in is returned as time of expiration instead of the number seconds until expiration
        refresh_request_body (Optional[Mapping[str, Any]]): The request body to send in the refresh request
        grant_type: The grant_type to request for access_token. If set to refresh_token, the refresh_token parameter has to be provided
        message_repository (MessageRepository): the message repository used to emit logs on HTTP requests
    """

    token_refresh_endpoint: Union[InterpolatedString, str]
    client_id: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    refresh_token: Optional[Union[InterpolatedString, str]] = None
    scopes: Optional[List[str]] = None
    token_expiry_date: Optional[Union[InterpolatedString, str]] = None
    _token_expiry_date: Optional[pendulum.DateTime] = field(init=False, repr=False, default=None)
    token_expiry_date_format: Optional[str] = None
    token_expiry_is_time_of_expiration: bool = False
    access_token_name: Union[InterpolatedString, str] = "access_token"
    expires_in_name: Union[InterpolatedString, str] = "expires_in"
    refresh_request_body: Optional[Mapping[str, Any]] = None
    grant_type: Union[InterpolatedString, str] = "refresh_token"
    message_repository: MessageRepository = NoopMessageRepository()

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__()
        self._token_refresh_endpoint = InterpolatedString.create(self.token_refresh_endpoint, parameters=parameters)
        self._client_id = InterpolatedString.create(self.client_id, parameters=parameters)
        self._client_secret = InterpolatedString.create(self.client_secret, parameters=parameters)
        if self.refresh_token is not None:
            self._refresh_token = InterpolatedString.create(self.refresh_token, parameters=parameters)
        else:
            self._refresh_token = None
        self.access_token_name = InterpolatedString.create(self.access_token_name, parameters=parameters)
        self.expires_in_name = InterpolatedString.create(self.expires_in_name, parameters=parameters)
        self.grant_type = InterpolatedString.create(self.grant_type, parameters=parameters)
        self._refresh_request_body = InterpolatedMapping(self.refresh_request_body or {}, parameters=parameters)
        self._token_expiry_date: pendulum.DateTime = (
            pendulum.parse(InterpolatedString.create(self.token_expiry_date, parameters=parameters).eval(self.config))  # type: ignore # pendulum.parse returns a datetime in this context
            if self.token_expiry_date
            else pendulum.now().subtract(days=1)  # type: ignore # substract does not have type hints
        )
        self._access_token: Optional[str] = None  # access_token is initialized by a setter

        if self.get_grant_type() == "refresh_token" and self._refresh_token is None:
            raise ValueError("OAuthAuthenticator needs a refresh_token parameter if grant_type is set to `refresh_token`")

    def get_token_refresh_endpoint(self) -> str:
        refresh_token: str = self._token_refresh_endpoint.eval(self.config)
        if not refresh_token:
            raise ValueError("OAuthAuthenticator was unable to evaluate token_refresh_endpoint parameter")
        return refresh_token

    def get_client_id(self) -> str:
        client_id: str = self._client_id.eval(self.config)
        if not client_id:
            raise ValueError("OAuthAuthenticator was unable to evaluate client_id parameter")
        return client_id

    def get_client_secret(self) -> str:
        client_secret: str = self._client_secret.eval(self.config)
        if not client_secret:
            raise ValueError("OAuthAuthenticator was unable to evaluate client_secret parameter")
        return client_secret

    def get_refresh_token(self) -> Optional[str]:
        return None if self._refresh_token is None else self._refresh_token.eval(self.config)

    def get_scopes(self) -> List[str]:
        return self.scopes or []

    def get_access_token_name(self) -> str:
        return self.access_token_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_expires_in_name(self) -> str:
        return self.expires_in_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_grant_type(self) -> str:
        return self.grant_type.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body.eval(self.config)  # type: ignore # eval should return a Mapping in this context

    def get_token_expiry_date(self) -> pendulum.DateTime:
        return self._token_expiry_date  # type: ignore # _token_expiry_date is a pendulum.DateTime. It is never None despite what mypy thinks

    def set_token_expiry_date(self, value: Union[str, int]) -> None:
        self._token_expiry_date = self._parse_token_expiration_date(value)

    @property
    def access_token(self) -> str:
        if self._access_token is None:
            raise ValueError("access_token is not set")
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = value

    @property
    def _message_repository(self) -> MessageRepository:
        """
        Overriding AbstractOauth2Authenticator._message_repository to allow for HTTP request logs
        """
        return self.message_repository


@dataclass
class DeclarativeSingleUseRefreshTokenOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator, DeclarativeAuthenticator):
    """
    Declarative version of SingleUseRefreshTokenOauth2Authenticator which can be used in declarative connectors.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
