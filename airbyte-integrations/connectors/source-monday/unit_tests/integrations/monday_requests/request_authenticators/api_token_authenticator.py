# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .authenticator import Authenticator


class ApiTokenAuthenticator(Authenticator):
    def __init__(self, api_token: str) -> None:
        super().__init__()
        self._api_token = api_token

    @property
    def client_access_token(self) -> str:
        return f"Bearer {self._api_token}"
