#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import time

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator, TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class AccessTokenAuthenticator(AbstractHeaderAuthenticator):
    """
    https://docs.railz.ai/reference/authentication
    """

    url = "https://auth.railz.ai/getAccess"
    refresh_after = 60  # minutes

    def __init__(self, client_id: str, secret_key: str):
        self._basic_auth = BasicHttpAuthenticator(username=client_id, password=secret_key)
        self._timestamp = time.time()
        self._token_auth = None

    def check_token(self):
        if not self._token_auth or time.time() - self._timestamp > self.refresh_after * 60:
            headers = {"accept": "application/json", **self._basic_auth.get_auth_header()}
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            self._token_auth = TokenAuthenticator(token=response_json["access_token"])
            self._timestamp = time.time()

    @property
    def auth_header(self) -> str:
        self.check_token()
        return self._token_auth._auth_header

    @property
    def token(self) -> str:
        self.check_token()
        return self._token_auth.token
