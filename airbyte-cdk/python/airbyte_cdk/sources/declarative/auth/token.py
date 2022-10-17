#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class ApiKeyAuthenticator(AbstractHeaderAuthenticator):
    """
    ApiKeyAuth sets a request header on the HTTP requests sent.

    The header is of the form:
    `"<header>": "<token>"`

    For example,
    `ApiKeyAuthenticator("Authorization", "Bearer hello")`
    will result in the following header set on the HTTP request
    `"Authorization": "Bearer hello"`

    """

    def __init__(
        self,
        header: Union[InterpolatedString, str],
        token: Union[InterpolatedString, str],
        config: Config,
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param header: Header key to set on the HTTP requests
        :param token: Header value to set on the HTTP requests
        :param config: The user-provided configuration as specified by the source's spec
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._header = InterpolatedString.create(header, options=options)
        self._token = InterpolatedString.create(token, options=options)
        self._config = config

    @property
    def auth_header(self) -> str:
        return self._header.eval(self._config)

    @property
    def token(self) -> str:
        return self._token.eval(self._config)


class BearerAuthenticator(AbstractHeaderAuthenticator):
    """
    Authenticator that sets the Authorization header on the HTTP requests sent.

    The header is of the form:
    `"Authorization": "Bearer <token>"`
    """

    def __init__(self, token: Union[InterpolatedString, str], config: Config, **options: Optional[Mapping[str, Any]]):
        """
        :param token: The bearer token
        :param config: The user-provided configuration as specified by the source's spec
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._token = InterpolatedString.create(token, options=options)
        self._config = config

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self._token.eval(self._config)}"


class BasicHttpAuthenticator(AbstractHeaderAuthenticator):
    """
    Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    The header is of the form
    `"Authorization": "Basic <encoded_credentials>"`
    """

    def __init__(
        self,
        username: Union[InterpolatedString, str],
        config: Config,
        password: Union[InterpolatedString, str] = "",
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param username: The username
        :param config: The user-provided configuration as specified by the source's spec
        :param password: The password
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._username = InterpolatedString.create(username, options=options)
        self._password = InterpolatedString.create(password, options=options)
        self._config = config

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        auth_string = f"{self._username.eval(self._config)}:{self._password.eval(self._config)}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        return f"Basic {b64_encoded}"
