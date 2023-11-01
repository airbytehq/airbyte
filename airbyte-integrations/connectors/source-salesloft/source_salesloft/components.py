from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class SalesloftAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    token_auth: BearerAuthenticator
    oauth2: DeclarativeSingleUseRefreshTokenOauth2Authenticator

    def __new__(cls, token_auth, oauth2, config, *args, **kwargs):
        print(config["credentials"])
        if config["credentials"]["auth_type"] == "api_key":
            return token_auth
        return oauth2
