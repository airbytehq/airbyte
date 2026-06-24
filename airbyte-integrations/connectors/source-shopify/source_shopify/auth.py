#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import (
    SingleUseRefreshTokenOauth2Authenticator,
)


class MissingAccessTokenError(Exception):
    """
    Raised when the token is `None` instead of the real value
    """


class NotImplementedAuth(Exception):
    """Not implemented Auth option error"""

    logger = logging.getLogger("airbyte")

    def __init__(self, auth_method: str = None):
        self.message = f"Not implemented Auth method = {auth_method}"
        super().__init__(self.logger.error(self.message))


class ShopifyAuthenticator(TokenAuthenticator):
    """
    Making Authenticator to be able to accept Header-Based authentication.
    """

    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def get_auth_header(self) -> Mapping[str, Any]:
        auth_header: str = "X-Shopify-Access-Token"
        credentials: Dict = self.config.get("credentials", self.config.get("auth_method"))
        auth_method: str = credentials.get("auth_method")

        if auth_method in ["oauth2.0", "access_token"]:
            access_token = credentials.get("access_token")
            if access_token:
                return {auth_header: access_token}
            else:
                raise MissingAccessTokenError
        elif auth_method == "api_password":
            return {auth_header: credentials.get("api_password")}
        else:
            raise NotImplementedAuth(auth_method)


class ShopifyOAuth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    """Authenticator for Shopify OAuth2.0 with expiring, rotating refresh tokens.

    Shopify requires the `X-Shopify-Access-Token` header instead of the standard
    `Authorization: Bearer` header used by the CDK's default OAuth authenticator.
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        token = self.access_token if self._is_access_token_flow else self.get_access_token()
        return {"X-Shopify-Access-Token": token}


def build_shopify_authenticator(config: Mapping[str, Any]) -> TokenAuthenticator:
    """Return the appropriate authenticator based on credentials in the config.

    For OAuth2.0 with a `refresh_token` present (expiring token flow), returns a
    `ShopifyOAuth2Authenticator` that handles automatic token refresh and rotation.
    For all other auth methods, returns the static `ShopifyAuthenticator`.
    """
    credentials: Dict = config.get("credentials", config.get("auth_method", {}))
    auth_method: str = credentials.get("auth_method", "")

    if auth_method == "oauth2.0" and credentials.get("refresh_token"):
        shop = config.get("shop", "")
        return ShopifyOAuth2Authenticator(
            connector_config=config,
            token_refresh_endpoint=f"https://{shop}.myshopify.com/admin/oauth/access_token",
            access_token_config_path=("credentials", "access_token"),
            refresh_token_config_path=("credentials", "refresh_token"),
            token_expiry_date_config_path=("credentials", "token_expiry_date"),
            client_id=credentials.get("client_id"),
            client_secret=credentials.get("client_secret"),
        )

    return ShopifyAuthenticator(config)
