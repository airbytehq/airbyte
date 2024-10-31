# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Sink factories for stream sinks."""

from __future__ import annotations

import abc
from typing import Any

from airbyte_cdk.destinations.sinks.base import StreamSinkBase
from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
)
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sql.shared import CatalogProvider

Record = Any


class StreamSinkFactoryBase(abc.ABC):
    """Base class for stream sink factories."""

    default_stream_sink_class: type[StreamSinkBase] = StreamSinkBase

    def create_sink(
        self,
        destination_config: dict,
        stream_name: str,
        stream_namespace: str,
        catalog_provider: CatalogProvider | ConfiguredAirbyteCatalog,
        message_repository: MessageRepository,
    ) -> StreamSinkBase:
        """Create a new stream sink instance.

        By default, this method creates a new instance of the default stream sink class.

        Subclasses can override this method to use a different stream sink class, for
        instance if different stream names or catalog configurations require different
        sink implementations.
        """
        return self.default_stream_sink_class(
            stream_name=stream_name,
            destination_config=destination_config,
            stream_namespace=stream_namespace,
            catalog_provider=catalog_provider,
            message_repository=message_repository,
        )
