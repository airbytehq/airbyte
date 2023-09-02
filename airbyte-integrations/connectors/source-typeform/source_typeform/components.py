#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator


@dataclass
class TypeformAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    token_auth: BearerAuthenticator
    oauth2: DeclarativeOauth2Authenticator

    def __new__(cls, token_auth, oauth2, config, *args, **kwargs):
        if config["credentials"]["access_token"]:
            return token_auth
        return oauth2
        