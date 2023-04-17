from typing import Mapping, Optional, Union
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Any
import requests


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(self, credentials_craft_host: str, credentials_craft_token: str, credentials_craft_token_id: int, check_connection: bool = False, raise_exception_on_check: bool = False):
        self._cc_host = credentials_craft_host
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id
        if check_connection:
            self.check_connection(raise_exception=raise_exception_on_check)

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/yandex/{self._cc_token_id}/"

    @property
    def _service_access_token(self) -> Mapping[str, Any]:
        resp = requests.get(self._url, headers={
                            "Authorization": f"Bearer {self._cc_token}"}).json()
        return resp.get("access_token")

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._service_access_token, "OAuth", "Authorization")
        return super().get_auth_header()

    def check_connection(self, raise_exception: bool = False) -> tuple[bool, Union[str, None]]:
        error = None
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            error = f"Connection to {self._cc_host} timed out"

        if not error:
            token_resp: dict[str, Any] = requests.get(
                self._url, headers={"Authorization": f"Bearer {self._cc_token}"}).json()
            if token_resp.get("error"):
                error = token_resp.get('error')

        if error:
            error = f'CredentialsCraft Error: {error}'
            if raise_exception:
                raise Exception(error)
            else:
                return False, error
        return True, None
