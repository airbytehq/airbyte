from typing import Mapping
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Any
import requests


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(
        self,
        credentials_craft_host: str,
        credentials_craft_token: str,
        credentials_craft_token_id: int,
    ):
        self._cc_host = credentials_craft_host.rstrip("/")
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id
        self._token = None

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/vk_ads/{self._cc_token_id}/"

    @property
    def token(self) -> str:
        response = requests.get(
            self._url,
            headers={"Authorization": f"Bearer {self._cc_token}"},
        )
        data: dict[str, Any] = response.json()
        return data.get("access_token")

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._token, "Bearer", "Authorization")
        if self.auth_header:
            auth_header = {self.auth_header: f"{self._auth_method} {self.token}"}
        else:
            auth_header = {}
        return auth_header

    def check_connection(self) -> tuple[bool, str]:
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            return False, f"Connection to {self._cc_host} timed out"

        data: dict[str, Any] = requests.get(
            self._url,
            headers={"Authorization": f"Bearer {self._cc_token}"},
        ).json()
        if data.get("error"):
            return False, f"CredentialsCraft error: {data.get('error')}"

        return True, None
