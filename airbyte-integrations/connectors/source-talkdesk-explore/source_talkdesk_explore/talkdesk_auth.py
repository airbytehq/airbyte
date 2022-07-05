#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, Dict, Mapping

import requests


class TalkdeskAuth:
    """Main class for handling Talkdesk Authentication.
    Only 'client_credentials' auth method supported at the moment.

    # TODO: Implement 'Signed JWT' and 'Authorization Code' auth methods.

    Docs: https://docs.talkdesk.com/docs/authentication

    """

    def __init__(self, config: Mapping[str, Any]):
        self.api_key = config.get("api_key", None)
        self.auth_url = config.get("auth_url", None)

    def _encode_key(self, key: str) -> bytes:
        """Encode 'str' API key to bytes"""
        base64_bytes = base64.b64encode(key.encode("ascii"))
        return base64_bytes.decode("ascii")

    def request_bearer_token(self) -> Dict:
        headers = {
            "Authorization": f"Basic {self._encode_key(self.api_key)}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            response = requests.request(
                "POST",
                url=self.auth_url,
                headers=headers,
            )
        except Exception as exc:
            raise exc

        return response.json()
