#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from base_python.cdk.streams.auth.core import HttpAuthenticator


class TokenAuthenticator(HttpAuthenticator):
    def __init__(self, token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {self._token}"}
