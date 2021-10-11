#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Mapping, Any


class NotImplementedAuth(Exception):
    """ Not implemented Auth option error"""

    logger = AirbyteLogger()
    
    def __init__(self, auth_option: str = None):
        self.message = f"Not implemented Auth method = {auth_option}"
        super().__init__(self.logger.error(self.message))


class ShopifyAuthenticator(TokenAuthenticator):

    """
    Making Authenticator to be able to accept Header-Based authentication.
    """

    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def get_auth_header(self) -> Mapping[str, Any]:

        auth_header = "X-Shopify-Access-Token"
        auth_method = self.config["auth_method"]
        auth_option = auth_method.get("auth_option")

        if auth_option == "access_token":
            return {auth_header: auth_method.get("access_token")}
        elif auth_option == "api_password":
            return {auth_header: auth_method.get("api_password")}
        else:
            raise NotImplementedAuth(auth_option)
