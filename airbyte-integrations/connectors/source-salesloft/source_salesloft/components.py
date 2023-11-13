from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator


@dataclass
class SalesloftAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    token_auth: BearerAuthenticator
    oauth2: DeclarativeSingleUseRefreshTokenOauth2Authenticator

    def __new__(cls, token_auth, oauth2, config, *args, **kwargs):
        if config["credentials"]["auth_type"] == "api_key":
            return token_auth
        return oauth2
