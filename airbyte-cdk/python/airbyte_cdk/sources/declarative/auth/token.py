#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.types import Config
from cachetools import TTLCache, cached


@dataclass
class ApiKeyAuthenticator(DeclarativeAuthenticator):
    """
    ApiKeyAuth sets a request header on the HTTP requests sent.

    The header is of the form:
    `"<header>": "<token>"`

    For example,
    `ApiKeyAuthenticator("Authorization", "Bearer hello")`
    will result in the following header set on the HTTP request
    `"Authorization": "Bearer hello"`

    Attributes:
        header (Union[InterpolatedString, str]): Header key to set on the HTTP requests
        api_token (Union[InterpolatedString, str]): Header value to set on the HTTP requests
        config (Config): The user-provided configuration as specified by the source's spec
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    request_option: RequestOption
    api_token: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._field_name = InterpolatedString.create(self.request_option.field_name, parameters=parameters)
        self._token = InterpolatedString.create(self.api_token, parameters=parameters)

    @property
    def auth_header(self) -> str:
        options = self._get_request_options(RequestOptionType.header)
        return next(iter(options.keys()), "")

    @property
    def token(self) -> str:
        return self._token.eval(self.config)

    def _get_request_options(self, option_type: RequestOptionType):
        options = {}
        if self.request_option.inject_into == option_type:
            options[self._field_name.eval(self.config)] = self.token
        return options

    def get_request_params(self) -> Optional[Mapping[str, Any]]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def get_request_body_data(self) -> Optional[Union[Mapping[str, Any], str]]:
        return self._get_request_options(RequestOptionType.body_data)

    def get_request_body_json(self) -> Optional[Mapping[str, Any]]:
        return self._get_request_options(RequestOptionType.body_json)


@dataclass
class BearerAuthenticator(DeclarativeAuthenticator):
    """
    Authenticator that sets the Authorization header on the HTTP requests sent.

    The header is of the form:
    `"Authorization": "Bearer <token>"`

    Attributes:
        api_token (Union[InterpolatedString, str]): The bearer token
        config (Config): The user-provided configuration as specified by the source's spec
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    api_token: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._token = InterpolatedString.create(self.api_token, parameters=parameters)

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self._token.eval(self.config)}"


@dataclass
class BasicHttpAuthenticator(DeclarativeAuthenticator):
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

    def __post_init__(self, parameters):
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
cacheSessionTokenAuthenticator = TTLCache(maxsize=1000, ttl=86400)


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
    return response.json()[response_key]


@dataclass
class SessionTokenAuthenticator(DeclarativeAuthenticator):
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

    def __post_init__(self, parameters):
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
        return self._header.eval(self.config)

    @property
    def token(self) -> str:
        if self._session_token.eval(self.config):
            if self.is_valid_session_token():
                return self._session_token.eval(self.config)
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
