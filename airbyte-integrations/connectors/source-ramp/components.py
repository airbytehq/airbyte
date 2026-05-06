#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import base64
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeOauth2Authenticator


@dataclass
class RampOauthAuthenticator(DeclarativeOauth2Authenticator):
    """
    Ramp's `/developer/v1/token` endpoint requires `Authorization: Basic <b64(client_id:client_secret)>`
    on the token request and, for `grant_type=client_credentials`, a singular space-separated `scope`
    field in the body. The CDK's default `OAuthAuthenticator` posts client credentials in the body and
    serializes scopes under the plural key `scopes` as a JSON list, neither of which match Ramp's
    documented contract.
    """

    def build_refresh_request_headers(self) -> Mapping[str, Any]:
        token = base64.b64encode(f"{self.get_client_id()}:{self.get_client_secret()}".encode("ascii")).decode("ascii")
        headers: MutableMapping[str, Any] = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        configured = self.get_refresh_request_headers()
        if configured:
            headers.update(configured)
        return headers

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {self.get_grant_type_name(): self.get_grant_type()}
        scopes = self.get_scopes()
        if scopes:
            payload["scope"] = " ".join(scopes)
        configured_body = self.get_refresh_request_body()
        if configured_body:
            for key, value in configured_body.items():
                if key not in payload:
                    payload[key] = value
        return payload
