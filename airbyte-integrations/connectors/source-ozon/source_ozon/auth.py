import logging
from typing import Optional, Dict, Tuple

import requests
from pydantic import BaseModel, SecretStr

from source_ozon.types import IsSuccess, Message

log = logging.getLogger(__name__)


class OzonToken(BaseModel):
    client_id: SecretStr
    client_secret: SecretStr
    access_token: SecretStr
    expires_in: int
    token_type: str


def fetch_ozon_token(client_id: str, client_secret: str) -> OzonToken:
    url = "https://performance.ozon.ru/api/client/token"
    try:
        response = requests.post(url, json={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"})
        response.raise_for_status()
        token = OzonToken(client_id=client_id, client_secret=client_secret, **response.json())
        log.info(f"Fetched Ozon authorization token. Expires in {token.expires_in} sec")
        return token
    except Exception as e:
        log.error(f"Failed to fetch Ozon token: {str(e)}")
        raise


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

    def __call__(self) -> OzonToken:
        token_resp = requests.get(self.url, headers=self.headers).json()
        token_data = token_resp["token"]["token_data"]
        client_id = token_data["client_id"]
        client_secret = token_data["client_secret"]
        return fetch_ozon_token(client_id, client_secret)

    def check_connection(self) -> Tuple[IsSuccess, Optional[Message]]:
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            if (status_code := resp.status_code) == 200:
                return True, None
            return False, f"Status code: {status_code}. Body: {resp.text}."
        except Exception as e:
            return False, str(e)
