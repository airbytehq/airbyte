#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator


class ZuoraAuthenticator(Oauth2Authenticator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload["grant_type"] = "client_credentials"
        payload.pop("refresh_token")  # Zuora doesn't have Refresh Token parameter
        return payload
