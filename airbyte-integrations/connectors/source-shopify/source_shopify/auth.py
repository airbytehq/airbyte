#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from typing import Any, Dict, Mapping, Optional

import requests

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


logger = logging.getLogger("airbyte")


class MissingAccessTokenError(Exception):
    """
    Raised when the token is `None` instead of the real value
    """


class ClientCredentialsTokenError(Exception):
    """
    Raised when there is an error exchanging client credentials for an access token
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotImplementedAuth(Exception):
    """Not implemented Auth option error"""

    logger = logging.getLogger("airbyte")

    def __init__(self, auth_method: str = None):
        self.message = f"Not implemented Auth method = {auth_method}"
        super().__init__(self.logger.error(self.message))


class ShopifyAuthenticator(TokenAuthenticator):
    """
    Making Authenticator to be able to accept Header-Based authentication.
    Supports OAuth2.0, API Password, and Client Credentials Grant authentication methods.
    """

    TOKEN_REFRESH_BUFFER_SECONDS = 300

    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None

    def _get_shop_name(self) -> str:
        """Extract the shop name from the config, removing .myshopify.com suffix if present."""
        shop = self.config.get("shop", "")
        return shop.replace(".myshopify.com", "")

    def _exchange_credentials_for_token(self) -> tuple:
        """
        Exchange client credentials for an access token using Shopify's Client Credentials Grant.
        See: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/client-credentials-grant
        """
        credentials = self.config.get("credentials", {})
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        shop = self._get_shop_name()

        if not client_id or not client_secret:
            raise ClientCredentialsTokenError("Missing client_id or client_secret in credentials")

        url = f"https://{shop}.myshopify.com/admin/oauth/access_token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 401:
                raise ClientCredentialsTokenError("Invalid client credentials. Please verify your Client ID and Client Secret.")
            elif response.status_code == 403:
                raise ClientCredentialsTokenError(
                    "Access denied. Please ensure your app is installed on the store and has the required scopes."
                )
            elif response.status_code == 404:
                raise ClientCredentialsTokenError(f"Store '{shop}' not found. Please verify your shop name.")
            else:
                raise ClientCredentialsTokenError(f"HTTP error {response.status_code} while exchanging client credentials.")
        except requests.exceptions.RequestException:
            raise ClientCredentialsTokenError("Network error while exchanging client credentials. Please check your network connection.")

        try:
            result = response.json()
            access_token = result["access_token"]
            expires_in = result.get("expires_in", 86399)
            expiry_time = time.time() + expires_in
            return access_token, expiry_time
        except (KeyError, ValueError):
            raise ClientCredentialsTokenError("Invalid response from Shopify token endpoint. Missing or malformed access_token.")

    def _get_client_credentials_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        Tokens are refreshed proactively before expiry to avoid mid-sync failures.
        """
        should_refresh = (
            self._access_token is None or self._token_expiry is None or time.time() > self._token_expiry - self.TOKEN_REFRESH_BUFFER_SECONDS
        )

        if should_refresh:
            logger.info("Refreshing client credentials access token...")
            self._access_token, self._token_expiry = self._exchange_credentials_for_token()

        return self._access_token

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
        elif auth_method == "client_credentials":
            access_token = self._get_client_credentials_token()
            return {auth_header: access_token}
        else:
            raise NotImplementedAuth(auth_method)
