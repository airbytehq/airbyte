#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping
from urllib import parse

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

logger = logging.getLogger("airbyte")


class Auth0Oauth2Authenticator(Oauth2Authenticator):
    def __init__(self, base_url: str, audience: str, client_id: str, client_secret: str):
        super().__init__(parse.urljoin(base_url, "/oauth/token"), client_id, client_secret, "")
        self.audience = audience.rstrip("/") + "/"

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        if not self.get_refresh_token():
            return {
                "grant_type": "client_credentials",
                "client_id": self.get_client_id(),
                "client_secret": self.get_client_secret(),
                "audience": self.audience,
            }
        else:
            return super().build_refresh_request_body()
