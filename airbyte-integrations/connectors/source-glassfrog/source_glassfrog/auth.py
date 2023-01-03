#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class GlassfrogAuthenticator(TokenAuthenticator):
    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Auth-Token": self.config.get("api_key", "")}
