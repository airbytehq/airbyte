#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from itertools import cycle
from typing import Any, List, Mapping

from deprecated import deprecated

from .core import HttpAuthenticator


@deprecated(version="0.1.20", reason="Use airbyte_cdk.sources.streams.http.requests_native_auth.TokenAuthenticator instead")
class TokenAuthenticator(HttpAuthenticator):
    def __init__(self, token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {self._token}"}


@deprecated(version="0.1.20", reason="Use airbyte_cdk.sources.streams.http.requests_native_auth.MultipleTokenAuthenticator instead")
class MultipleTokenAuthenticator(HttpAuthenticator):
    def __init__(self, tokens: List[str], auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._tokens = tokens
        self._tokens_iter = cycle(self._tokens)

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {next(self._tokens_iter)}"}
