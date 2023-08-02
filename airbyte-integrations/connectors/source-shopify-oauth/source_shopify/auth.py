#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class NotImplementedAuth(Exception):
    """Not implemented Auth option error"""

    logger = AirbyteLogger()

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
            return {auth_header: credentials.get("access_token")}
        elif auth_method == "api_password":
            return {auth_header: credentials.get("api_password")}
        else:
            raise NotImplementedAuth(auth_method)
