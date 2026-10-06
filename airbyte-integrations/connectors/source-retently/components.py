#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator


@dataclass
class AuthenticatorRetently(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    api_auth: ApiKeyAuthenticator
    oauth: DeclarativeOauth2Authenticator

    def __new__(cls, api_auth, oauth, config, *args, **kwargs):
        if config["credentials"]["api_key"]:
            return api_auth
        else:
            return oauth
