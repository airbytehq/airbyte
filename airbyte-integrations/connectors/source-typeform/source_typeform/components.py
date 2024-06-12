#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class TypeformAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    token_auth: BearerAuthenticator
    oauth2: DeclarativeSingleUseRefreshTokenOauth2Authenticator

    def __new__(cls, token_auth, oauth2, config, *args, **kwargs):
        return token_auth if config["credentials"]["auth_type"] == "access_token" else oauth2


@dataclass
class FormIdPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        form_ids = self.config.get("form_ids", [])

        if form_ids:
            for item in form_ids:
                yield StreamSlice(partition={"form_id": item}, cursor_slice={})
        else:
            for parent_stream_config in self.parent_stream_configs:
                for item in parent_stream_config.stream.read_records(sync_mode=SyncMode.full_refresh):
                    yield StreamSlice(partition={"form_id": item["id"]}, cursor_slice={})

        yield from []
