# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

API_KEY = "test-key"
API_TOKEN = "test-token"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"
REFRESH_TOKEN = "refresh-token-1"
START_DATE = "2024-01-01T00:00:00Z"


class ConfigBuilder:
    """Builds configs in the flat shape of versions before 1.4.0 unless a `credentials` method is called."""

    def __init__(self) -> None:
        self._config: dict = {"key": API_KEY, "token": API_TOKEN, "start_date": START_DATE}

    def with_board_ids(self, board_ids: list[str]) -> "ConfigBuilder":
        self._config["board_ids"] = board_ids
        return self

    def with_api_key_credentials(self) -> "ConfigBuilder":
        self._config.pop("key")
        self._config.pop("token")
        self._config["credentials"] = {"auth_type": "api_key", "key": API_KEY, "token": API_TOKEN}
        return self

    def with_oauth_credentials(self, access_token: str | None = None, token_expiry_date: str | None = None) -> "ConfigBuilder":
        self._config.pop("key")
        self._config.pop("token")
        credentials = {
            "auth_type": "oauth2.0",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
        }
        if access_token:
            credentials["access_token"] = access_token
        if token_expiry_date:
            credentials["token_expiry_date"] = token_expiry_date
        self._config["credentials"] = credentials
        return self

    def build(self) -> dict:
        return {key: dict(value) if isinstance(value, dict) else value for key, value in self._config.items()}
