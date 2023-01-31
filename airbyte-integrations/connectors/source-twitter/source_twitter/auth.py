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
        return f"{self._host}/api/v1/token/twitter/{self._twitter_token_id}/"

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._bearer_token}"}

    def _get_app_secret_url(self, app_secret_id: int) -> str:
        return f"{self._host}/api/v1/oauth_app/twitter/{app_secret_id}/"

    def __call__(self) -> TwitterCredentials:
        token_resp = requests.get(self.url, headers=self.headers).json()
        app_secret_id = token_resp["app_secret"]
        app_secret_url = self._get_app_secret_url(app_secret_id)
        app_secret_resp = requests.get(app_secret_url, headers=self.headers).json()
        return {
            "consumer_key": app_secret_resp["client_id"],
            "consumer_secret": app_secret_resp["client_secret"],
            "access_token": token_resp["access_token"],
            "access_token_secret": token_resp["oauth_token_secret"],
        }

    def check_connection(self) -> tuple[IsSuccess, Optional[Message]]:
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            if (status_code := resp.status_code) == 200:
                return True, None
            return False, f"Status code: {status_code}. Body: {resp.text}."
        except Exception as e:
            return False, str(e)
