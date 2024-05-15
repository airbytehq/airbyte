#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Tuple

import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class CustomBearerAuthenticator(DeclarativeAuthenticator):
    """
    Custom authenticator that uses "SSWS" instead of "Bearer" in the authorization header.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"SSWS {self.config['credentials']['api_token']}"


@dataclass
class CustomOauth2Authenticator(DeclarativeOauth2Authenticator):
    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"SSWS {self.get_access_token()}"

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"SSWS {self.get_access_token()}"}

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                auth=(self.client_id, self.client_secret),
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
