#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from itertools import cycle
from typing import List

from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import (
    AbstractHeaderAuthenticator,
)


class MultipleTokenAuthenticator(AbstractHeaderAuthenticator):
    """
    Builds auth header, based on the list of tokens provided.
    Auth header is changed per each `get_auth_header` call, using each token in cycle.
    The token is attached to each request via the `auth_header` header.
    """

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        return f"{self._auth_method} {next(self._tokens_iter)}"

    def __init__(
        self, tokens: List[str], auth_method: str = "Bearer", auth_header: str = "Authorization"
    ):
        self._auth_method = auth_method
        self._auth_header = auth_header
        self._tokens = tokens
        self._tokens_iter = cycle(self._tokens)


class TokenAuthenticator(AbstractHeaderAuthenticator):
    """
    Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.
    """

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        return f"{self._auth_method} {self._token}"

    def __init__(self, token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self._auth_header = auth_header
        self._auth_method = auth_method
        self._token = token


class BasicHttpAuthenticator(AbstractHeaderAuthenticator):
    """
    Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme
    """

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        return f"{self._auth_method} {self._token}"

    def __init__(
        self,
        username: str,
        password: str = "",
        auth_method: str = "Basic",
        auth_header: str = "Authorization",
    ):
        auth_string = f"{username}:{password}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        self._auth_header = auth_header
        self._auth_method = auth_method
        self._token = b64_encoded
