from typing import Any, Mapping
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import requests


class DatacraftAuth(TokenAuthenticator):
    def __init__(self, user_url_base: str, username: str, password: str):
        super().__init__(None)
        self._username = username
        self._password = password
        self._user_url_base = user_url_base
        self.token = None

    @property
    def is_logged_in(self) -> bool:
        return bool(self.token)

    def login(self):
        url = self._user_url_base + "/api/v1/login/"
        response = requests.post(url, json={"username": self._username, "password": self._password})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception("Login failed. Please check your credentials.")
        self.token = response.headers["Set-Cookie"]

    def get_auth_header(self) -> Mapping[str, Any]:
        if not self.is_logged_in:
            self.login()
        return {"Cookie": self.token}
