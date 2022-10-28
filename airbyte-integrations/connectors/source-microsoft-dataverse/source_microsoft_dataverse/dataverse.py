#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator


class MicrosoftOauth2Authenticator(Oauth2Authenticator):
    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request
        """
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "scope": self.get_scopes(),
        }

        return payload


def get_auth(config: Mapping[str, Any]) -> MicrosoftOauth2Authenticator:
    return MicrosoftOauth2Authenticator(
        token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
        client_id=config["client_id"],
        client_secret=config["client_secret_value"],
        scopes=[f'{config["url"]}/.default'],
        refresh_token="",
    )


def do_request(config: Mapping[str, Any], path: str):
    auth = get_auth(config)
    headers = auth.get_auth_header()
    # Call a protected API with the access token.
    return requests.get(
        config["url"] + "/api/data/v9.2/" + path,
        headers=headers,
    )
