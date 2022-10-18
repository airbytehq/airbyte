#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ApiKeyAuthenticator(AbstractHeaderAuthenticator, DeclarativeAuthenticator, JsonSchemaMixin):
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
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    header: Union[InterpolatedString, str]
    api_token: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._header = InterpolatedString.create(self.header, options=options)
        self._token = InterpolatedString.create(self.api_token, options=options)

    @property
    def auth_header(self) -> str:
        return self._header.eval(self.config)

    @property
    def token(self) -> str:
        return self._token.eval(self.config)


@dataclass
class BearerAuthenticator(AbstractHeaderAuthenticator, DeclarativeAuthenticator, JsonSchemaMixin):
    """
    Authenticator that sets the Authorization header on the HTTP requests sent.

    The header is of the form:
    `"Authorization": "Bearer <token>"`

    Attributes:
        api_token (Union[InterpolatedString, str]): The bearer token
        config (Config): The user-provided configuration as specified by the source's spec
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    api_token: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._token = InterpolatedString.create(self.api_token, options=options)

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self._token.eval(self.config)}"


@dataclass
class BasicHttpAuthenticator(AbstractHeaderAuthenticator, DeclarativeAuthenticator, JsonSchemaMixin):
    """
    Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using base64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    The header is of the form
    `"Authorization": "Basic <encoded_credentials>"`

    Attributes:
        username (Union[InterpolatedString, str]): The username
        config (Config): The user-provided configuration as specified by the source's spec
        password (Union[InterpolatedString, str]): The password
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    username: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    password: Union[InterpolatedString, str] = ""

    def __post_init__(self, options):
        self._username = InterpolatedString.create(self.username, options=options)
        self._password = InterpolatedString.create(self.password, options=options)

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        auth_string = f"{self._username.eval(self.config)}:{self._password.eval(self.config)}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        return f"Basic {b64_encoded}"
