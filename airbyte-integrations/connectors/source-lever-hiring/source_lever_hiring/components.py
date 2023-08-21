#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator


@dataclass
class AuthenticatorLeverHiring(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    basic_auth: BasicHttpAuthenticator
    oauth2: DeclarativeOauth2Authenticator

    def __new__(cls, basic_auth, oauth2, config, *args, **kwargs):
        if config["credentials"]["api_key"]:
            return basic_auth
        else:
            return oauth2