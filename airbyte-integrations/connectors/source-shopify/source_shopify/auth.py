#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping, Union

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
        credentials: Mapping[str, Any] = self.config.get("credentials", self.config.get("auth_method"))
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
        return {"X-Shopify-Access-Token": self.get_access_token()}


def build_shopify_authenticator(config: Mapping[str, Any]) -> Union[ShopifyAuthenticator, ShopifyOAuth2Authenticator]:
    """Return the appropriate authenticator based on credentials in the config.

    For OAuth2.0 with a `refresh_token` present (expiring token flow), returns a
    `ShopifyOAuth2Authenticator` that handles automatic token refresh and rotation.
    For all other auth methods, returns the static `ShopifyAuthenticator`.
    """
    credentials: Mapping[str, Any] = config.get("credentials", config.get("auth_method", {}))
    auth_method: str = credentials.get("auth_method", "")

    if auth_method == "oauth2.0" and credentials.get("refresh_token"):
        shop = config.get("shop", "")
        # Snapshot the user config so the authenticator owns a clean copy. The caller stores
        # the returned authenticator (and other runtime-only keys) back into `config`, and the
        # CDK serializes `connector_config` when emitting the refreshed-token control message;
        # sharing the same dict would put a non-JSON-serializable authenticator object into that
        # payload and crash the refresh.
        connector_config = {key: value for key, value in config.items() if key not in ("authenticator", "shop_id")}
        return ShopifyOAuth2Authenticator(
            connector_config=connector_config,
            token_refresh_endpoint=f"https://{shop}.myshopify.com/admin/oauth/access_token",
            access_token_config_path=("credentials", "access_token"),
            refresh_token_config_path=("credentials", "refresh_token"),
            token_expiry_date_config_path=("credentials", "token_expiry_date"),
            client_id=credentials.get("client_id"),
            client_secret=credentials.get("client_secret"),
            refresh_token_error_status_codes=(400, 401),
            refresh_token_error_key="error",
            refresh_token_error_values=("invalid_grant", "invalid_request"),
        )

    return ShopifyAuthenticator(config)
