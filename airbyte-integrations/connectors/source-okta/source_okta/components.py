#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import time
import uuid
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Tuple

import jwt
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


@dataclass
class CustomOauth2PrivateKeyAuthenticator(DeclarativeAuthenticator):
    """
    Custom authenticator that uses a signed JWT with a private key to authenticate against Okta.
    """

    config: Config

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        domain = self.config["domain"]
        client_id = self.config["credentials"]["client_id"]
        key_id = self.config["credentials"]["key_id"]
        private_key = self.config["credentials"]["private_key"]
        scope = self.config["credentials"]["scope"]
        now = int(time.time())

        jwt_payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": f"https://{domain}.okta.com/oauth2/v1/token",
            "iat": now,
            "exp": now + 3600,
            "jti": str(uuid.uuid4()),
        }
        jwt_headers = {"kid": key_id, "alg": "RS256"}

        client_assertion = jwt.encode(jwt_payload, private_key, algorithm="RS256", headers=jwt_headers)
        token_url = f"https://{domain}.okta.com/oauth2/v1/token"
        token_response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": client_assertion,
                "scope": scope,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            response = token_response.json()
            return f"Bearer {response['access_token']}"
        except Exception as e:
            raise Exception(f"Error while getting access token: {e}") from e
