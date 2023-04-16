#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Tuple

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator


class CriteoAuthenticator(Oauth2Authenticator):
    def __init__(self, config: Mapping):

        super().__init__(
            token_refresh_endpoint="https://api.criteo.com/oauth2/token",
            client_secret=config["client_secret"],
            client_id=config["client_id"],
            refresh_token=None,
        )

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Calling the Google OAuth 2.0 token endpoint. Used for authorizing signed JWT.
        Returns tuple with access token and token's time-to-live
        """
        response_json = None
        try:
            payload = "grant_type=client_credentials&client_id={}&client_secret={}".format(self.get_client_id(), self.get_client_secret())
            headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}

            response = requests.request(method="POST", url=self.get_token_refresh_endpoint(), data=payload, headers=headers)

            response_json = response.json()
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if response_json and "error" in response_json:
                raise Exception(
                    "Error refreshing access token {}. Error: {}; Error details: {}; Exception: {}".format(
                        response_json, response_json["error"], response_json["error_description"], e
                    )
                ) from e
            raise Exception(f"Error refreshing access token: {e}") from e
        else:
            return response_json["access_token"], response_json["expires_in"]
