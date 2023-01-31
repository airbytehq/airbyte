from typing import Mapping
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Any
import requests


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(self, credentials_craft_host: str, credentials_craft_token: str, credentials_craft_mytarget_token_id: int):
        if credentials_craft_host.endswith("/"):
            credentials_craft_host = credentials_craft_host[:-1]
        self._cc_host = credentials_craft_host
        self._cc_token = credentials_craft_token
        self._cc_mytarget_token_id = credentials_craft_mytarget_token_id

    @property
    def _mytarget_access_token(self) -> Mapping[str, Any]:
        response = requests.get(
            f"{self._cc_host}/api/v1/token/mytarget/{self._cc_mytarget_token_id}/", headers={"Authorization": f"Bearer {self._cc_token}"}
        )
        try:
            return response.json()["access_token"]
        except:
            print(response.text)
            raise Exception(f"CC Api Error: {response.text}")

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._mytarget_access_token, "Bearer", "Authorization")
        return super().get_auth_header()

    def check_connection(self):
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            return False, f"Connection to {self._cc_host} timed out"

        token_resp = requests.get(
            f"{self._cc_host}/api/v1/token/mytarget/{self._cc_mytarget_token_id}/", headers={"Authorization": f"Bearer {self._cc_token}"}
        ).json()
        if token_resp.get("error"):
            return False, f"CredentialsCraft error: {token_resp.get('error')}"

        return True, None
