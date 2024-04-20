# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import base64

from .authenticator import Authenticator


class ApiTokenAuthenticator(Authenticator):
    def __init__(self, email: str, password: str) -> None:
        super().__init__()
        self._email = f"{email}/token"
        self._password = password

    @property
    def client_access_token(self) -> str:
        api_token = base64.b64encode(f"{self._email}:{self._password}".encode("utf-8"))
        return f"Basic {api_token.decode('utf-8')}"
