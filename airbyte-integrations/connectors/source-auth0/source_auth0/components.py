#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator


@dataclass
class AuthenticatorAuth0(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    bearer: BearerAuthenticator
    oauth: DeclarativeOauth2Authenticator

    def __new__(cls, bearer, oauth, config, *args, **kwargs):
        auth_type = config.get("credentials", {}).get("auth_type")
        if auth_type == "oauth2_access_token":
            return bearer
        elif auth_type == "oauth2_confidential_application":
            return oauth
        else:
            raise Exception("Not possible configure Auth method")
