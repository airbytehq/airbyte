from typing import Optional

import requests

from source_twitter.types import IsSuccess, Message, TwitterCredentials


class CredentialsCraftAuthenticator:
    def __init__(self, host: str, bearer_token: str, twitter_token_id: int):
        self._host = host
        self._bearer_token = bearer_token
        self._twitter_token_id = twitter_token_id

    @property
    def url(self) -> str:
        return f"{self._host}/api/v1/token/twitter/{self._twitter_token_id}/json/"

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._bearer_token}"}

    def __call__(self) -> TwitterCredentials:
        token_resp = requests.get(self.url, headers=self.headers).json()
        token_data = token_resp["token"]
        return {
            "consumer_key": token_data["consumer_key"],
            "consumer_secret": token_data["consumer_secret"],
            "access_token": token_data["access_token"],
            "access_token_secret": token_data["access_token_secret"],
        }

    def check_connection(self) -> tuple[IsSuccess, Optional[Message]]:
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            if (status_code := resp.status_code) == 200:
                return True, None
            return False, f"Status code: {status_code}. Body: {resp.text}."
        except Exception as e:
            return False, str(e)
