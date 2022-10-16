#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Tuple

import requests
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator


class AsanaOauth2Authenticator(Oauth2Authenticator):
    """
    Unlike most Oauth services that accept oauth parameters in form of json
    encoded body, Asana's oauth token endpoint expects oauth parameters to be
    in form-encoded post body.
    https://developers.asana.com/docs/oauth
    """

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Override base refresh_access_token method to send form-encoded oauth
        parameters over POST request body.
        Returns:
            Tuple of access token and expiration time in seconds
        """
        data = {
            "client_id": (None, self.client_id),
            "client_secret": (None, self.client_secret),
            "grant_type": (None, "refresh_token"),
            "refresh_token": (None, self.refresh_token),
        }

        response = requests.post(self.token_refresh_endpoint, files=data)
        response.raise_for_status()
        response_body = response.json()
        return response_body["access_token"], response_body["expires_in"]
