#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.requests_native_auth import (
    BasicHttpAuthenticator,
    SingleUseRefreshTokenOauth2Authenticator,
    TokenAuthenticator,
)
from airbyte_cdk.utils import AirbyteTracedException


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
        content = response.json()
        if response.status_code == 400 and content.get("error") == "invalid_grant":
            raise AirbyteTracedException(
                internal_message=content.get("error_description"),
                message="Refresh token is invalid or expired. Please re-authenticate to restore access to Airtable.",
                failure_type=FailureType.config_error,
            )
        response.raise_for_status()
        return content


class AirtableAuth:
    def __new__(cls, config: dict) -> Union[TokenAuthenticator, AirtableOAuth]:
        # for old configs with api_key provided
        if "api_key" in config:
            return TokenAuthenticator(token=(config or {}).get("api_key"))
        # for new oauth configs
        credentials = config["credentials"]
        if credentials["auth_method"] == "oauth2.0":
            return AirtableOAuth(config, "https://airtable.com/oauth2/v1/token")
        elif credentials["auth_method"] == "api_key":
            return TokenAuthenticator(token=credentials["api_key"])
