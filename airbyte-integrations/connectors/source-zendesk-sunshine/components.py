#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator


@dataclass
class AuthenticatorZendeskSunshine(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    basic_auth: BasicHttpAuthenticator
    oauth2: BearerAuthenticator
    oauth2_refresh: DeclarativeSingleUseRefreshTokenOauth2Authenticator

    def __new__(cls, basic_auth, oauth2, oauth2_refresh, config, *args, **kwargs):
        credentials = config.get("credentials", {})
        auth_method = credentials.get("auth_method", "")
        if auth_method == "api_token":
            return basic_auth
        elif auth_method == "oauth2_refresh":
            return oauth2_refresh
        else:
            return oauth2
