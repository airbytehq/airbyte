# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"
INITIAL_REFRESH_TOKEN = "refresh-token-1"


class ConfigBuilder:
    """Builder for source-outreach test configurations."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": INITIAL_REFRESH_TOKEN,
            "redirect_uri": "https://example.com/callback",
            "start_date": "2024-01-01T00:00:00Z",
        }

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
