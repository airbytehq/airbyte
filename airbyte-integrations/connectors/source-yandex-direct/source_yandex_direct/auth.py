from typing import Mapping
from urllib import response
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Any
import requests


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(self, credentials_craft_host: str, credentials_craft_token: str, credentials_craft_token_id: int):
        self._cc_host = credentials_craft_host.rstrip("/")
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/yandex/{self._cc_token_id}/"

    @property
    def _service_access_token(self) -> Mapping[str, Any]:
        resp = requests.get(self._url, headers={"Authorization": f"Bearer {self._cc_token}"}).json()
        return resp.get("access_token")

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._service_access_token, "Bearer", "Authorization")
        return super().get_auth_header()

    def check_connection(self):
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            return False, f"Connection to {self._cc_host} timed out"

        token_resp = requests.get(self._url, headers={"Authorization": f"Bearer {self._cc_token}"})
        print("token_resp.request.url", token_resp.request.url)
        try:
            token_resp_data = token_resp.json()
            if token_resp_data.get("error"):
                return False, f"CredentialsCraft error: {token_resp.get('error')}"
        except Exception as e:
            return False, f"Check bearer error: {e}; {token_resp}; Body: {token_resp.text}"
        return True, None
