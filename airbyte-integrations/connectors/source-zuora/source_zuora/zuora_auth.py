#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator

from .zuora_endpoint import get_url_base


class OAuth(Oauth2Authenticator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload["grant_type"] = "client_credentials"
        payload.pop("refresh_token")  # Zuora doesn't have Refresh Token parameter
        return payload


class ZuoraAuthenticator:
    def __init__(self, config: Dict):
        self.config = config

    @property
    def url_base(self) -> str:
        return get_url_base(self.config["tenant_endpoint"])

    def get_auth(self) -> OAuth:
        return OAuth(
            token_refresh_endpoint=f"{self.url_base}/oauth/token",
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            refresh_token=None,  # Zuora doesn't have Refresh Token parameter
        )
