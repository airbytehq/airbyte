#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Union

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import (
    BasicHttpAuthenticator,
    SingleUseRefreshTokenOauth2Authenticator,
    TokenAuthenticator,
)


class AirtableOAuth(SingleUseRefreshTokenOauth2Authenticator):
    """
    https://airtable.com/developers/web/api/oauth-reference#token-expiry-refresh-tokens
    """

    def build_refresh_request_headers(self) -> Mapping[str, Any]:
        """
        https://airtable.com/developers/web/api/oauth-reference#token-refresh-request-headers
        """
        return {
            "Authorization": BasicHttpAuthenticator(self.get_client_id(), self.get_client_secret()).token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        https://airtable.com/developers/web/api/oauth-reference#token-refresh-request-body
        """
        return {
            "grant_type": self.get_grant_type(),
            "refresh_token": self.get_refresh_token(),
        }

    def _get_refresh_access_token_response(self) -> Mapping[str, Any]:
        response = requests.request(
            method="POST",
            url=self.get_token_refresh_endpoint(),
            data=self.build_refresh_request_body(),
            headers=self.build_refresh_request_headers(),
        )
        response.raise_for_status()
        return response.json()


class AirtableAuth:
    def __new__(cls, config: dict) -> Union[TokenAuthenticator, AirtableOAuth]:
        # for old configs with api_key provided
        if "api_key" in config:
            return TokenAuthenticator(token=(config or {}).get("api_key"))
        # for new oauth configs
        return AirtableOAuth(config, "https://airtable.com/oauth2/v1/token")
