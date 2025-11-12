# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, final

from airbyte import exceptions as exc
from airbyte_cdk.models import DestinationSyncMode

if TYPE_CHECKING:
    from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream


class CatalogProvider:
    """A catalog provider wraps a configured catalog and configured streams.

    This class is responsible for providing information about the catalog and streams.

    Note:
    - The catalog provider is not responsible for managing the catalog or streams but it may
      be updated with new streams as they are discovered.
    """

    def __init__(
        self,
        configured_catalog: ConfiguredAirbyteCatalog,
    ) -> None:
        """Initialize the catalog manager with a catalog object reference.

        Since the catalog is passed by reference, the catalog manager may be updated with new
        streams as they are discovered.
        """
        self._catalog: ConfiguredAirbyteCatalog = configured_catalog

    @property
    def configured_catalog(self) -> ConfiguredAirbyteCatalog:
        return self._catalog

    @property
    def stream_names(self) -> list[str]:
        return list({stream.stream.name for stream in self.configured_catalog.streams})

    def get_configured_stream_info(
        self,
        stream_name: str,
    ) -> ConfiguredAirbyteStream:
        """Return the column definitions for the given stream."""
        if not self.configured_catalog:
            raise exc.PyAirbyteInternalError(
                message="Cannot get stream JSON schema without a catalog.",
            )

        matching_streams: list[ConfiguredAirbyteStream] = [
            stream
            for stream in self.configured_catalog.streams
            if stream.stream.name == stream_name
        ]
        if not matching_streams:
            raise exc.AirbyteStreamNotFoundError(
                stream_name=stream_name,
                context={
                    "available_streams": [
                        stream.stream.name for stream in self.configured_catalog.streams
                    ],
                },
            )

        if len(matching_streams) > 1:
            raise exc.PyAirbyteInternalError(
                message="Multiple streams found with same name.",
                context={
                    "stream_name": stream_name,
                },
            )

        return matching_streams[0]

    @final
    def get_stream_json_schema(
        self,
        stream_name: str,
    ) -> dict[str, Any]:
        """Return the column definitions for the given stream."""
        return self.get_configured_stream_info(stream_name).stream.json_schema

    def get_stream_properties(
        self,
        stream_name: str,
    ) -> dict[str, dict]:
        """Return the names of the top-level properties for the given stream."""
        return self.get_stream_json_schema(stream_name)["properties"]

    def get_destination_sync_mode(
        self,
        stream_name: str,
    ) -> DestinationSyncMode:
        """Return the destination sync mode for the given stream."""
        return self.get_configured_stream_info(stream_name).destination_sync_mode
