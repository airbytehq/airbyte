from typing import Any, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class CalltouchAuthenticator(TokenAuthenticator):
    """
    Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.
    """

    @property
    def auth_header(self) -> str:
        return self._auth_header

    def get_auth_header(self) -> Mapping[str, Any]:
        headers = super().get_auth_header()
        if self.additional_headers:
            headers.update(self.additional_headers)
        return headers

    @property
    def token(self) -> str:
        return self._token

    def __init__(
        self,
        token: str,
        auth_method: str = "Bearer",
        auth_header: str = "Authorization",
        additional_headers: Optional[dict] = None,
    ):
        super().__init__(token, auth_method, auth_header)
        self.additional_headers = additional_headers if additional_headers is not None else {}


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(
        self,
        credentials_craft_host: str,
        credentials_craft_token: str,
        credentials_craft_token_id: int,
        additional_headers: dict = {},
    ):
        self._cc_host = credentials_craft_host.rstrip("/")
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id
        self._token = None
        self.additional_headers = additional_headers

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/static/{self._cc_token_id}/"

    @property
    def token(self) -> str:
        response = requests.get(
            self._url,
            headers={"Authorization": f"Bearer {self._cc_token}"},
        )
        data: dict[str, Any] = response.json()
        print("data", data)
        return data["token_data"]["access_token"]

    def get_auth_header(self) -> Mapping[str, Any]:
        super().__init__(self._token, "Bearer", "Authorization")
        if self.auth_header:
            auth_header = {self.auth_header: f"{self._auth_method} {self.token}"}
        else:
            auth_header = {}
        if self.additional_headers:
            auth_header.update(self.additional_headers)
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
