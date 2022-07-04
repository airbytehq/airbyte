#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from itertools import cycle
from typing import Any, List, Mapping

from requests.auth import AuthBase


class MultipleTokenAuthenticator(AuthBase):
    """
    Builds auth header, based on the list of tokens provided.
    Auth header is changed per each `get_auth_header` call, using each token in cycle.
    The token is attached to each request via the `auth_header` header.
    """

    def __init__(self, tokens: List[str], auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._tokens = tokens
        self._tokens_iter = cycle(self._tokens)

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {next(self._tokens_iter)}"}


class TokenAuthenticator(MultipleTokenAuthenticator):
    """
    Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.
    """

    def __init__(self, token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        super().__init__([token], auth_method, auth_header)


class BasicHttpAuthenticator(TokenAuthenticator):
    """
    Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme
    """

    def __init__(self, username: str, password: str, auth_method: str = "Basic", auth_header: str = "Authorization"):
        auth_string = f"{username}:{password}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(b64_encoded, auth_method, auth_header)
