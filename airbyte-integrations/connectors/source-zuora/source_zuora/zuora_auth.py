#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator

from .zuora_endpoint import get_url_base
class ZuoraAuthenticator(Oauth2Authenticator):
    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint=f"{get_url_base(config['tenant_endpoint'])}/oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=None,
        )
        self._url_base = get_url_base(config['tenant_endpoint']).rstrip("/") + "/"

    @property
    def url_base(self) -> str:
        return self._url_base

    def get_refresh_request_params(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="GET", url=self._url_base + "oauth/token", params=self.get_refresh_request_params())
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


