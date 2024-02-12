import logging
from typing import Any

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

# Enable debug mode for requests
logging.basicConfig(level=logging.DEBUG)


# import http

# http.client.HTTPConnection.debuglevel = 1


class VkusvillPasswordAuth(TokenAuthenticator):
    def __init__(self, url_base: str, login: str, password: str):
        self._url_base = url_base.rstrip("/")
        self._login = login
        self._password = password
        super().__init__(self.authenticate()["DATA"]["token"])

    def authenticate(self) -> dict[str, Any]:
        """Return token data by username and password"""
        resp = requests.post(
            self._url_base + "/api/v1/auth/login",
            json={"email": self._login, "password": self._password},
        )
        # print("resp.text123", resp.text)
        resp.raise_for_status()
        return resp.json()
