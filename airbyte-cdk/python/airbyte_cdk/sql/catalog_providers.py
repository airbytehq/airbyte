# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, final

from airbyte_protocol.models import (
    ConfiguredAirbyteCatalog,
)

from airbyte import exceptions as exc
from airbyte._util.name_normalizers import LowerCaseNormalizer
from airbyte.strategies import WriteMethod, WriteStrategy


if TYPE_CHECKING:
    from airbyte_protocol.models import (
        ConfiguredAirbyteStream,
    )

    from airbyte.results import ReadResult


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
        self._catalog: ConfiguredAirbyteCatalog = self.validate_catalog(configured_catalog)

    @staticmethod
    def validate_catalog(catalog: ConfiguredAirbyteCatalog) -> None:
        """Validate the catalog to ensure it is valid.

        This requires ensuring that `generationId` and `minGenerationId` are both set. If
        not, both values will be set to `1`.
        """
        for stream in catalog.streams:
            if stream.generation_id is None:
                stream.generation_id = 1
            if stream.minimum_generation_id is None:
                stream.minimum_generation_id = 1
            if stream.sync_id is None:
                stream.sync_id = 1  # This should ideally increment monotonically with each sync.

        return catalog

    @property
    def configured_catalog(self) -> ConfiguredAirbyteCatalog:
        """Return the configured catalog."""
        return self._catalog

    @property
    def stream_names(self) -> list[str]:
        """Return the names of the streams in the catalog."""
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

    @classmethod
    def from_read_result(
        cls,
        read_result: ReadResult,
    ) -> CatalogProvider:
        """Create a catalog provider from a `ReadResult` object."""
        return cls(
            ConfiguredAirbyteCatalog(
                streams=[
                    dataset._stream_metadata  # noqa: SLF001  # Non-public API
                    for dataset in read_result.values()
                ]
            )
        )

    def get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str]:
        """Return the primary keys for the given stream."""
        pks = self.get_configured_stream_info(stream_name).primary_key
        if not pks:
            return []

        normalized_pks: list[list[str]] = [
            [LowerCaseNormalizer.normalize(c) for c in pk] for pk in pks
        ]

        for pk_nodes in normalized_pks:
            if len(pk_nodes) != 1:
                raise exc.AirbyteError(
                    message=(
                        "Nested primary keys are not supported. "
                        "Each PK column should have exactly one node. "
                    ),
                    context={
                        "stream_name": stream_name,
                        "primary_key_nodes": pk_nodes,
                    },
                )

        return [pk_nodes[0] for pk_nodes in normalized_pks]

    def get_cursor_key(
        self,
        stream_name: str,
    ) -> str | None:
        """Return the cursor key for the given stream."""
        return self.get_configured_stream_info(stream_name).cursor_field

    def resolve_write_method(
        self,
        stream_name: str,
        write_strategy: WriteStrategy,
    ) -> WriteMethod:
        """Return the write method for the given stream."""
        has_pks: bool = bool(self.get_primary_keys(stream_name))
        has_incremental_key: bool = bool(self.get_cursor_key(stream_name))
        if write_strategy == WriteStrategy.MERGE and not has_pks:
            raise exc.PyAirbyteInputError(
                message="Cannot use merge strategy on a stream with no primary keys.",
                context={
                    "stream_name": stream_name,
                },
            )

        if write_strategy != WriteStrategy.AUTO:
            return WriteMethod(write_strategy)

        if has_pks:
            return WriteMethod.MERGE

        if has_incremental_key:
            return WriteMethod.APPEND

        return WriteMethod.REPLACE

    def with_write_strategy(
        self,
        write_strategy: WriteStrategy,
    ) -> CatalogProvider:
        """Return a new catalog provider with the specified write strategy applied.

        The original catalog provider is not modified.
        """
        new_catalog: ConfiguredAirbyteCatalog = copy.deepcopy(self.configured_catalog)
        for stream in new_catalog.streams:
            write_method = self.resolve_write_method(
                stream_name=stream.stream.name,
                write_strategy=write_strategy,
            )
            stream.destination_sync_mode = write_method.destination_sync_mode

        return CatalogProvider(new_catalog)
