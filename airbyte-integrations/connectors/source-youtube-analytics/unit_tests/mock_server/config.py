#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional


CLIENT_ID = "test_client_id"
CLIENT_SECRET = "test_client_secret"
REFRESH_TOKEN = "test_refresh_token"


class ConfigBuilder:
    """Builder for `source-youtube-analytics` test configurations."""

    def __init__(self) -> None:
        self._client_id: str = CLIENT_ID
        self._client_secret: str = CLIENT_SECRET
        self._refresh_token: str = REFRESH_TOKEN
        self._content_owner_id: Optional[str] = None
        self._testing_period: Optional[str] = None

    def with_credentials(self, client_id: str, client_secret: str, refresh_token: str) -> "ConfigBuilder":
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        return self

    def with_content_owner_id(self, content_owner_id: str) -> "ConfigBuilder":
        """Set `content_owner_id`, which makes `ContentOwnerRequester` add `onBehalfOfContentOwner`."""
        self._content_owner_id = content_owner_id
        return self

    def with_testing_period(self, testing_period: str) -> "ConfigBuilder":
        """Set `testing_period` (an ISO-8601 duration), which pulls the cursor's `start_datetime` forward from 1990."""
        self._testing_period = testing_period
        return self

    def build(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "credentials": {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
            }
        }
        if self._content_owner_id:
            config["content_owner_id"] = self._content_owner_id
        if self._testing_period:
            config["testing_period"] = self._testing_period
        return config
