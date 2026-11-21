# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self) -> None:
        self._credentials = {
            "auth_type": "oauth2.0",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "old-refresh-token",
            "access_token": "old-access-token",
            "token_expiry_date": "2000-01-01T00:00:00Z",
        }

    def with_expiry(self, expiry: str) -> "ConfigBuilder":
        self._credentials["token_expiry_date"] = expiry
        return self

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._credentials = {"auth_type": "api_key", "api_key": api_key}
        return self

    def build(self) -> dict:
        return {"start_date": "2020-01-01T00:00:00Z", "credentials": dict(self._credentials)}
