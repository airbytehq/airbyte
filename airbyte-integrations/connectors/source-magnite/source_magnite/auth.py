#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from typing import Any, Mapping
import logging

# from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
   
# class MissingAccessTokenError(Exception):
#     """
#     Raised when the token is `None` instead of the real value
#     """


# class NotImplementedAuth(Exception):
#     """Not implemented Auth option error"""

#     logger = logging.getLogger("airbyte")

#     def __init__(self, auth_method: str = None):
#         self.message = f"Not implemented Auth method = {auth_method}"
#         super().__init__(self.logger.error(self.message))
url_base = "https://api.tremorhub.com/v1/resources/sessions"
DOMAIN = ".tremorhub.com"

class CookieAuthenticator(DeclarativeAuthenticator):

    def __init__(self, config):
        self.cookie_jar = self.login(config["access_key"], config["secret_key"])
        # self.url_base = url_base

    def login(self, access_key, secret_key):
        login_body = {
            "accessKey": access_key,
            "secretKey": secret_key
        }
        resp = requests.post(url=url_base, json=login_body)
        resp.raise_for_status()
        return resp.cookies

    def get_auth_header(self) -> Mapping[str, Any]:
        cookie_dict = self.cookie_jar.get_dict(domain=DOMAIN)
        auth_headers = {"Cookie": ";".join([f"{k}={v}" for k,v in cookie_dict.items()])}
        auth_headers["Content-Type"] = "application/json"
        return auth_headers
    