from typing import Optional, Dict, Tuple

import requests

from source_wildberries_ads.types import WildberriesCredentials, IsSuccess, Message


class CredentialsCraftAuthenticator:
    def __init__(self, host: str, bearer_token: str, token_id: int):
        self._host = host
        self._bearer_token = bearer_token
        self._token_id = token_id

    @property
    def url(self) -> str:
        return f"{self._host}/api/v1/token/static/{self._token_id}/json/"

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._bearer_token}"}

    def __call__(self) -> WildberriesCredentials:
        token_resp = requests.get(self.url, headers=self.headers).json()
        token_data = token_resp["token"]["token_data"]
        return {
            "api_key": token_data["api_key"],
            "type": token_data["type"],
        }

    def check_connection(self) -> Tuple[IsSuccess, Optional[Message]]:
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            if (status_code := resp.status_code) == 200:
                return True, None
            return False, f"Status code: {status_code}. Body: {resp.text}."
        except Exception as e:
            return False, str(e)
