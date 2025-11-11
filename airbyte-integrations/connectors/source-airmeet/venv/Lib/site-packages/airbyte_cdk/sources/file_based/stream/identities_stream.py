#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from functools import cache
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.file_based.config.file_based_stream_config import PrimaryKeyType
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedErrorsCollector
from airbyte_cdk.sources.file_based.file_based_stream_permissions_reader import (
    AbstractFileBasedStreamPermissionsReader,
)
from airbyte_cdk.sources.streams.core import JsonSchema
from airbyte_cdk.sources.streams.permissions.identities_stream import IdentitiesStream


class FileIdentitiesStream(IdentitiesStream):
    """
    The identities stream. A full refresh stream to sync identities from a certain domain.
    The stream reader manage the logic to get such data, which is implemented on connector side.
    """

    is_resumable = False

    def __init__(
        self,
        catalog_schema: Optional[Mapping[str, Any]],
        stream_permissions_reader: AbstractFileBasedStreamPermissionsReader,
        discovery_policy: AbstractDiscoveryPolicy,
        errors_collector: FileBasedErrorsCollector,
    ) -> None:
        super().__init__()
        self.catalog_schema = catalog_schema
        self.stream_permissions_reader = stream_permissions_reader
        self._discovery_policy = discovery_policy
        self.errors_collector = errors_collector
        self._cursor: MutableMapping[str, Any] = {}

    @property
    def primary_key(self) -> PrimaryKeyType:
        return None

    def load_identity_groups(self) -> Iterable[Dict[str, Any]]:
        return self.stream_permissions_reader.load_identity_groups(logger=self.logger)

    @cache
    def get_json_schema(self) -> JsonSchema:
        return self.stream_permissions_reader.identities_schema
