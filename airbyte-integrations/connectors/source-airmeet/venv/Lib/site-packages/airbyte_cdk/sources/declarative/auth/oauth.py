#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import (
    AbstractOauth2Authenticator,
)
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import (
    SingleUseRefreshTokenOauth2Authenticator,
)
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse

logger = logging.getLogger("airbyte")


@dataclass
class DeclarativeOauth2Authenticator(AbstractOauth2Authenticator, DeclarativeAuthenticator):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials based on
    a declarative connector configuration file. Credentials can be defined explicitly or via interpolation
    at runtime. The generated access token is attached to each request via the Authorization header.

    Attributes:
        token_refresh_endpoint (Union[InterpolatedString, str]): The endpoint to refresh the access token
        client_id (Union[InterpolatedString, str]): The client id
        client_secret (Union[InterpolatedString, str]): Client secret (can be empty for APIs that support this)
        refresh_token (Union[InterpolatedString, str]): The token used to refresh the access token
        access_token_name (Union[InterpolatedString, str]): THe field to extract access token from in the response
        expires_in_name (Union[InterpolatedString, str]): The field to extract expires_in from in the response
        config (Mapping[str, Any]): The user-provided configuration as specified by the source's spec
        scopes (Optional[List[str]]): The scopes to request
        token_expiry_date (Optional[Union[InterpolatedString, str]]): The access token expiration date
        token_expiry_date_format str: format of the datetime; provide it if expires_in is returned in datetime instead of seconds
        token_expiry_is_time_of_expiration bool: set True it if expires_in is returned as time of expiration instead of the number seconds until expiration
        refresh_request_body (Optional[Mapping[str, Any]]): The request body to send in the refresh request
        refresh_request_headers (Optional[Mapping[str, Any]]): The request headers to send in the refresh request
        grant_type: The grant_type to request for access_token. If set to refresh_token, the refresh_token parameter has to be provided
        message_repository (MessageRepository): the message repository used to emit logs on HTTP requests
    """

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    client_id: Optional[Union[InterpolatedString, str]] = None
    client_secret: Optional[Union[InterpolatedString, str]] = None
    token_refresh_endpoint: Optional[Union[InterpolatedString, str]] = None
    refresh_token: Optional[Union[InterpolatedString, str]] = None
    scopes: Optional[List[str]] = None
    token_expiry_date: Optional[Union[InterpolatedString, str]] = None
    _token_expiry_date: Optional[AirbyteDateTime] = field(init=False, repr=False, default=None)
    token_expiry_date_format: Optional[str] = None
    token_expiry_is_time_of_expiration: bool = False
    access_token_name: Union[InterpolatedString, str] = "access_token"
    access_token_value: Optional[Union[InterpolatedString, str]] = None
    client_id_name: Union[InterpolatedString, str] = "client_id"
    client_secret_name: Union[InterpolatedString, str] = "client_secret"
    expires_in_name: Union[InterpolatedString, str] = "expires_in"
    refresh_token_name: Union[InterpolatedString, str] = "refresh_token"
    refresh_request_body: Optional[Mapping[str, Any]] = None
    refresh_request_headers: Optional[Mapping[str, Any]] = None
    grant_type_name: Union[InterpolatedString, str] = "grant_type"
    grant_type: Union[InterpolatedString, str] = "refresh_token"
    message_repository: MessageRepository = NoopMessageRepository()
    profile_assertion: Optional[DeclarativeAuthenticator] = None
    use_profile_assertion: Optional[Union[InterpolatedBoolean, str, bool]] = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__()
        if self.token_refresh_endpoint is not None:
            self._token_refresh_endpoint: Optional[InterpolatedString] = InterpolatedString.create(
                self.token_refresh_endpoint, parameters=parameters
            )
        else:
            self._token_refresh_endpoint = None
        self._client_id_name = InterpolatedString.create(self.client_id_name, parameters=parameters)
        self._client_id = (
            InterpolatedString.create(self.client_id, parameters=parameters)
            if self.client_id
            else self.client_id
        )
        self._client_secret_name = InterpolatedString.create(
            self.client_secret_name, parameters=parameters
        )
        self._client_secret = (
            InterpolatedString.create(self.client_secret, parameters=parameters)
            if self.client_secret
            else self.client_secret
        )
        self._refresh_token_name = InterpolatedString.create(
            self.refresh_token_name, parameters=parameters
        )
        if self.refresh_token is not None:
            self._refresh_token: Optional[InterpolatedString] = InterpolatedString.create(
                self.refresh_token, parameters=parameters
            )
        else:
            self._refresh_token = None
        self.access_token_name = InterpolatedString.create(
            self.access_token_name, parameters=parameters
        )
        self.expires_in_name = InterpolatedString.create(
            self.expires_in_name, parameters=parameters
        )
        self.grant_type_name = InterpolatedString.create(
            self.grant_type_name, parameters=parameters
        )
        self.grant_type = InterpolatedString.create(
            "urn:ietf:params:oauth:grant-type:jwt-bearer"
            if self.use_profile_assertion
            else self.grant_type,
            parameters=parameters,
        )
        self._refresh_request_body = InterpolatedMapping(
            self.refresh_request_body or {}, parameters=parameters
        )
        self._refresh_request_headers = InterpolatedMapping(
            self.refresh_request_headers or {}, parameters=parameters
        )
        try:
            if (
                isinstance(self.token_expiry_date, (int, str))
                and str(self.token_expiry_date).isdigit()
            ):
                self._token_expiry_date = ab_datetime_parse(self.token_expiry_date)
            else:
                self._token_expiry_date = (
                    ab_datetime_parse(
                        InterpolatedString.create(
                            self.token_expiry_date, parameters=parameters
                        ).eval(self.config)
                    )
                    if self.token_expiry_date
                    else ab_datetime_now() - timedelta(days=1)
                )
        except ValueError as e:
            raise ValueError(f"Invalid token expiry date format: {e}")
        self.use_profile_assertion = (
            InterpolatedBoolean(self.use_profile_assertion, parameters=parameters)
            if isinstance(self.use_profile_assertion, str)
            else self.use_profile_assertion
        )
        self.assertion_name = "assertion"

        if self.access_token_value is not None:
            self._access_token_value = InterpolatedString.create(
                self.access_token_value, parameters=parameters
            ).eval(self.config)
        else:
            self._access_token_value = None

        self._access_token: Optional[str] = (
            self._access_token_value if self.access_token_value else None
        )

        if not self.use_profile_assertion and any(
            client_creds is None for client_creds in [self.client_id, self.client_secret]
        ):
            raise ValueError(
                "OAuthAuthenticator configuration error: Both 'client_id' and 'client_secret' are required for the "
                "basic OAuth flow."
            )
        if self.profile_assertion is None and self.use_profile_assertion:
            raise ValueError(
                "OAuthAuthenticator configuration error: 'profile_assertion' is required when using the profile assertion flow."
            )
        if self.get_grant_type() == "refresh_token" and self._refresh_token is None:
            raise ValueError(
                "OAuthAuthenticator configuration error: A 'refresh_token' is required when the 'grant_type' is set to 'refresh_token'."
            )

    def get_token_refresh_endpoint(self) -> Optional[str]:
        if self._token_refresh_endpoint is not None:
            refresh_token_endpoint: str = self._token_refresh_endpoint.eval(self.config)
            if not refresh_token_endpoint:
                raise ValueError(
                    "OAuthAuthenticator was unable to evaluate token_refresh_endpoint parameter"
                )
            return refresh_token_endpoint
        return None

    def get_client_id_name(self) -> str:
        return self._client_id_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_client_id(self) -> str:
        client_id = self._client_id.eval(self.config) if self._client_id else self._client_id
        if not client_id:
            raise ValueError("OAuthAuthenticator was unable to evaluate client_id parameter")
        return client_id  # type: ignore # value will be returned as a string, or an error will be raised

    def get_client_secret_name(self) -> str:
        return self._client_secret_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_client_secret(self) -> str:
        client_secret = (
            self._client_secret.eval(self.config) if self._client_secret else self._client_secret
        )
        if not client_secret:
            # We've seen some APIs allowing empty client_secret so we will only log here
            logger.warning(
                "OAuthAuthenticator was unable to evaluate client_secret parameter hence it'll be empty"
            )
        return client_secret  # type: ignore # value will be returned as a string, which might be empty

    def get_refresh_token_name(self) -> str:
        return self._refresh_token_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_refresh_token(self) -> Optional[str]:
        return None if self._refresh_token is None else str(self._refresh_token.eval(self.config))

    def get_scopes(self) -> List[str]:
        return self.scopes or []

    def get_access_token_name(self) -> str:
        return self.access_token_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_expires_in_name(self) -> str:
        return self.expires_in_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_grant_type_name(self) -> str:
        return self.grant_type_name.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_grant_type(self) -> str:
        return self.grant_type.eval(self.config)  # type: ignore # eval returns a string in this context

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body.eval(self.config)

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        return self._refresh_request_headers.eval(self.config)

    def get_token_expiry_date(self) -> AirbyteDateTime:
        if not self._has_access_token_been_initialized():
            return AirbyteDateTime.from_datetime(datetime.min)
        return self._token_expiry_date  # type: ignore # _token_expiry_date is an AirbyteDateTime. It is never None despite what mypy thinks

    def _has_access_token_been_initialized(self) -> bool:
        return self._access_token is not None

    def set_token_expiry_date(self, value: AirbyteDateTime) -> None:
        self._token_expiry_date = value

    def get_assertion_name(self) -> str:
        return self.assertion_name

    def get_assertion(self) -> str:
        if self.profile_assertion is None:
            raise ValueError("profile_assertion is not set")
        return self.profile_assertion.token

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request

        Override to define additional parameters
        """
        if self.use_profile_assertion:
            return {
                self.get_grant_type_name(): self.get_grant_type(),
                self.get_assertion_name(): self.get_assertion(),
            }
        return super().build_refresh_request_body()

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
class DeclarativeSingleUseRefreshTokenOauth2Authenticator(
    SingleUseRefreshTokenOauth2Authenticator, DeclarativeAuthenticator
):
    """
    Declarative version of SingleUseRefreshTokenOauth2Authenticator which can be used in declarative connectors.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
