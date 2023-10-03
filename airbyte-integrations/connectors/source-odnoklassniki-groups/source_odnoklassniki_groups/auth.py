from typing import Optional, Dict, Tuple

import requests
from pydantic import BaseModel, SecretStr

from source_odnoklassniki_groups.types import IsSuccess, Message


class OKCredentials(BaseModel):
    application_id: SecretStr
    application_key: SecretStr
    application_secret_key: SecretStr
    access_token: SecretStr
    session_secret_key: SecretStr


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

    def __call__(self) -> OKCredentials:
        token_resp = requests.get(self.url, headers=self.headers).json()
        token_data = token_resp["token"]["token_data"]
        return OKCredentials(**token_data)

    def check_connection(self) -> Tuple[IsSuccess, Optional[Message]]:
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            if (status_code := resp.status_code) == 200:
                return True, None
            return False, f"Status code: {status_code}. Body: {resp.text}."
        except Exception as e:
            return False, str(e)
