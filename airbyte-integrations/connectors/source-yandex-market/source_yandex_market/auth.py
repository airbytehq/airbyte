from typing import Mapping
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from typing import Any
import requests


class YandexMarketAuthenticator(TokenAuthenticator):
    def __init__(self, token: str, oauth_client_id: str):
        self._tokens = [token]
        self._oauth_client_id = oauth_client_id

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f'OAuth oauth_token="{self._tokens[0]}", oauth_client_id="{self._oauth_client_id}"'}


class CredentialsCraftAuthenticator(YandexMarketAuthenticator):
    def __init__(self, credentials_craft_host: str, credentials_craft_token: str, credentials_craft_token_id: int, oauth_client_id: str):
        self._cc_host = credentials_craft_host
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id
        self._oauth_client_id = oauth_client_id

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/yandex/{self._cc_token_id}/"

    @property
    def _service_access_token(self) -> Mapping[str, Any]:
        resp = requests.get(self._url, headers={"Authorization": f"Bearer {self._cc_token}"}).json()
        return resp.get("access_token")

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._service_access_token, self._oauth_client_id)
        return super().get_auth_header()

    def check_connection(self):
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            return False, f"Connection to {self._cc_host} timed out"

        token_resp = requests.get(self._url, headers={"Authorization": f"Bearer {self._cc_token}"}).json()
        if token_resp.get("error"):
            return False, f"CredentialsCraft error: {token_resp.get('error')}"

        return True, None
