
import requests
from functools import cached_property
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class RenewalSecretKeyAuthenticator(AbstractHeaderAuthenticator):
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

    def renew(self):
        self._token = self.get_token()

    def __init__(self, secret_key: str, refresh_token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self._secret_key = secret_key
        self._refresh_token = refresh_token
        self._auth_header = auth_header
        self._auth_method = auth_method
        self._token = self.get_token()

    def get_token(self) -> str:
        headers = {
            "secretkey": self._secret_key,
            "refreshToken": self._refresh_token
        }

        url = f"https://platform.ironsrc.com/partners/publisher/auth"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        token = response.text.replace('"', "")
        return token
