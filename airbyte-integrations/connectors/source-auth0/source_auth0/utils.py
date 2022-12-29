#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from typing import Dict
from urllib import parse

from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
from requests.auth import AuthBase

from .authenticator import Auth0Oauth2Authenticator

logger = logging.getLogger("airbyte")


def get_api_endpoint(url_base: str, version: str) -> str:
    return parse.urljoin(url_base, f"/api/{version}/")


def initialize_authenticator(config: Dict) -> AuthBase:
    credentials = config.get("credentials")
    if not credentials:
        raise Exception("Config validation error. `credentials` not specified.")

    auth_type = credentials.get("auth_type")
    if not auth_type:
        raise Exception("Config validation error. `auth_type` not specified.")

    if auth_type == "oauth2_access_token":
        return TokenAuthenticator(credentials.get("access_token"))

    if auth_type == "oauth2_confidential_application":
        return Auth0Oauth2Authenticator(
            base_url=config.get("base_url"),
            audience=credentials.get("audience"),
            client_secret=credentials.get("client_secret"),
            client_id=credentials.get("client_id"),
        )


def datetime_to_string(date: datetime.datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
