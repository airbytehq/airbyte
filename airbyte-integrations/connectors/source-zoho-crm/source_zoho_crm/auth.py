#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping, Tuple

import requests

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


class ZohoOauth2Authenticator(Oauth2Authenticator):
    def _prepare_refresh_token_params(self) -> Dict[str, str]:
        return {
            "refresh_token": self.get_refresh_token(),
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "grant_type": "refresh_token",
        }

    def get_auth_header(self) -> Mapping[str, Any]:
        token = self.get_access_token()
        return {"Authorization": f"Zoho-oauthtoken {token}"}

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        This method is overridden because token parameters should be passed via URL params, not via the request payload.
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="POST", url=self.get_token_refresh_endpoint(), params=self._prepare_refresh_token_params())
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.get_access_token_name()], response_json[self.get_expires_in_name()]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
