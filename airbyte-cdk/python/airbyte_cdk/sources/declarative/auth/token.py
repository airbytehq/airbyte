#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from dataclasses import InitVar, dataclass
from typing import Any, Callable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider, SessionTokenProvider, TokenProvider
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ApiKeyAuthenticator as ApiKeyAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BasicHttpAuthenticator as BasicHttpAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BearerAuthenticator as BearerAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    LegacySessionTokenAuthenticator as LegacySessionTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.types import Config
from cachetools import TTLCache, cached
from pydantic.v1 import BaseModel


@dataclass
class ApiKeyAuthenticator(DeclarativeAuthenticator, ComponentConstructor):
    """
    ApiKeyAuth sets a request header on the HTTP requests sent.

    The header is of the form:
    `"<header>": "<token>"`

    For example,
    `ApiKeyAuthenticator("Authorization", "Bearer hello")`
    will result in the following header set on the HTTP request
    `"Authorization": "Bearer hello"`

    Attributes:
        request_option (RequestOption): request option how to inject the token into the request
        token_provider (TokenProvider): Provider of the token
        config (Config): The user-provided configuration as specified by the source's spec
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    request_option: RequestOption
    token_provider: TokenProvider
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: ApiKeyAuthenticatorModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        token_provider: Optional[TokenProvider] = None,
        **kwargs: Any,
    ) -> Optional[Mapping[str, Any]]:
        if model.inject_into is None and model.header is None:
            raise ValueError("Expected either inject_into or header to be set for ApiKeyAuthenticator")

        if model.inject_into is not None and model.header is not None:
            raise ValueError("inject_into and header cannot be set both for ApiKeyAuthenticator - remove the deprecated header option")

        if token_provider is not None and model.api_token != "":
            raise ValueError("If token_provider is set, api_token is ignored and has to be set to empty string.")

        request_option = (
            RequestOption(
                inject_into=RequestOptionType(model.inject_into.inject_into.value),
                field_name=model.inject_into.field_name,
                parameters=model.parameters or {},
            )
            if model.inject_into
            else RequestOption(
                inject_into=RequestOptionType.header,
                field_name=model.header or "",
                parameters=model.parameters or {},
            )
        )

        return {
            "token_provider": token_provider
            if token_provider is not None
            else InterpolatedStringTokenProvider(api_token=model.api_token or "", config=config, parameters=model.parameters or {}),
            "request_option": request_option,
            "config": config,
            "parameters": model.parameters or {},
        }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._field_name = InterpolatedString.create(self.request_option.field_name, parameters=parameters)

    @property
    def auth_header(self) -> str:
        options = self._get_request_options(RequestOptionType.header)
        return next(iter(options.keys()), "")

    @property
    def token(self) -> str:
        return self.token_provider.get_token()

    def _get_request_options(self, option_type: RequestOptionType) -> Mapping[str, Any]:
        options = {}
        if self.request_option.inject_into == option_type:
            options[self._field_name.eval(self.config)] = self.token
        return options

    def get_request_params(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def get_request_body_data(self) -> Union[Mapping[str, Any], str]:
        return self._get_request_options(RequestOptionType.body_data)

    def get_request_body_json(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_json)


@dataclass
class BearerAuthenticator(DeclarativeAuthenticator, ComponentConstructor):
    """
    Authenticator that sets the Authorization header on the HTTP requests sent.

    The header is of the form:
    `"Authorization": "Bearer <token>"`

    Attributes:
        token_provider (TokenProvider): Provider of the token
        config (Config): The user-provided configuration as specified by the source's spec
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    token_provider: TokenProvider
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: BearerAuthenticatorModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        token_provider: Optional[TokenProvider] = None,
        **kwargs: Any,
    ) -> Optional[Mapping[str, Any]]:
        if token_provider is not None and model.api_token != "":
            raise ValueError("If token_provider is set, api_token is ignored and has to be set to empty string.")
        return {
            "token_provider": token_provider
            if token_provider is not None
            else InterpolatedStringTokenProvider(api_token=model.api_token or "", config=config, parameters=model.parameters or {}),
            "config": config,
            "parameters": model.parameters or {},
        }

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self.token_provider.get_token()}"


@dataclass
class BasicHttpAuthenticator(DeclarativeAuthenticator, ComponentConstructor):
    """
    Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using base64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    The header is of the form
    `"Authorization": "Basic <encoded_credentials>"`

    Attributes:
        username (Union[InterpolatedString, str]): The username
        config (Config): The user-provided configuration as specified by the source's spec
        password (Union[InterpolatedString, str]): The password
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    username: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    password: Union[InterpolatedString, str] = ""

    @classmethod
    def resolve_dependencies(
        cls,
        model: BasicHttpAuthenticatorModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[Mapping[str, Any]]:
        return {
            "username": model.username,
            "config": config,
            "parameters": model.parameters or {},
            "password": model.password,
        }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._username = InterpolatedString.create(self.username, parameters=parameters)
        self._password = InterpolatedString.create(self.password, parameters=parameters)

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        auth_string = f"{self._username.eval(self.config)}:{self._password.eval(self.config)}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        return f"Basic {b64_encoded}"


"""
    maxsize - The maximum size of the cache
    ttl - time-to-live value in seconds
    docs https://cachetools.readthedocs.io/en/latest/
    maxsize=1000 - when the cache is full, in this case more than 1000,
    i.e. by adding another item the cache would exceed its maximum size, the cache must choose which item(s) to discard
    ttl=86400 means that cached token will live for 86400 seconds (one day)
"""
cacheSessionTokenAuthenticator: TTLCache[str, str] = TTLCache(maxsize=1000, ttl=86400)


@cached(cacheSessionTokenAuthenticator)
def get_new_session_token(api_url: str, username: str, password: str, response_key: str) -> str:
    """
    This method retrieves session token from api by username and password for SessionTokenAuthenticator.
    It's cashed to avoid a multiple calling by sync and updating session token every stream sync.
    Args:
        api_url: api url for getting new session token
        username: username for auth
        password: password for auth
        response_key: field name in response to retrieve a session token

    Returns:
        session token
    """
    response = requests.post(
        f"{api_url}",
        headers={"Content-Type": "application/json"},
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    if not response.ok:
        raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
    return str(response.json()[response_key])


@dataclass
class LegacySessionTokenAuthenticator(DeclarativeAuthenticator, ComponentConstructor):
    """
    Builds auth based on session tokens.
    A session token is a random value generated by a server to identify
    a specific user for the duration of one interaction session.

    The header is of the form
    `"Specific Header": "Session Token Value"`

    Attributes:
        api_url (Union[InterpolatedString, str]): Base api url of source
        username (Union[InterpolatedString, str]): The username
        config (Config): The user-provided configuration as specified by the source's spec
        password (Union[InterpolatedString, str]): The password
        header (Union[InterpolatedString, str]): Specific header of source for providing session token
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
        session_token (Union[InterpolatedString, str]): Session token generated by user
        session_token_response_key (Union[InterpolatedString, str]): Key for retrieving session token from api response
        login_url (Union[InterpolatedString, str]): Url fot getting a specific session token
        validate_session_url (Union[InterpolatedString, str]): Url to validate passed session token
    """

    api_url: Union[InterpolatedString, str]
    header: Union[InterpolatedString, str]
    session_token: Union[InterpolatedString, str]
    session_token_response_key: Union[InterpolatedString, str]
    username: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    login_url: Union[InterpolatedString, str]
    validate_session_url: Union[InterpolatedString, str]
    password: Union[InterpolatedString, str] = ""

    @classmethod
    def resolve_dependencies(
        cls,
        model: LegacySessionTokenAuthenticatorModel,
        config: Config,
        url_base: str,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[Mapping[str, Any]]:
        return {
            "api_url": url_base,
            "header": model.header,
            "login_url": model.login_url,
            "password": model.password or "",
            "session_token": model.session_token or "",
            "session_token_response_key": model.session_token_response_key or "",
            "username": model.username or "",
            "validate_session_url": model.validate_session_url,
            "config": config,
            "parameters": model.parameters or {},
        }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._username = InterpolatedString.create(self.username, parameters=parameters)
        self._password = InterpolatedString.create(self.password, parameters=parameters)
        self._api_url = InterpolatedString.create(self.api_url, parameters=parameters)
        self._header = InterpolatedString.create(self.header, parameters=parameters)
        self._session_token = InterpolatedString.create(self.session_token, parameters=parameters)
        self._session_token_response_key = InterpolatedString.create(self.session_token_response_key, parameters=parameters)
        self._login_url = InterpolatedString.create(self.login_url, parameters=parameters)
        self._validate_session_url = InterpolatedString.create(self.validate_session_url, parameters=parameters)

        self.logger = logging.getLogger("airbyte")

    @property
    def auth_header(self) -> str:
        return str(self._header.eval(self.config))

    @property
    def token(self) -> str:
        if self._session_token.eval(self.config):
            if self.is_valid_session_token():
                return str(self._session_token.eval(self.config))
        if self._password.eval(self.config) and self._username.eval(self.config):
            username = self._username.eval(self.config)
            password = self._password.eval(self.config)
            session_token_response_key = self._session_token_response_key.eval(self.config)
            api_url = f"{self._api_url.eval(self.config)}{self._login_url.eval(self.config)}"

            self.logger.info("Using generated session token by username and password")
            return get_new_session_token(api_url, username, password, session_token_response_key)

        raise ConnectionError("Invalid credentials: session token is not valid or provide username and password")

    def is_valid_session_token(self) -> bool:
        try:
            response = requests.get(
                f"{self._api_url.eval(self.config)}{self._validate_session_url.eval(self.config)}",
                headers={self.auth_header: self._session_token.eval(self.config)},
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes["unauthorized"]:
                self.logger.info(f"Unable to connect by session token from config due to {str(e)}")
                return False
            else:
                raise ConnectionError(f"Error while validating session token: {e}")
        if response.ok:
            self.logger.info("Connection check for source is successful.")
            return True
        else:
            raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
