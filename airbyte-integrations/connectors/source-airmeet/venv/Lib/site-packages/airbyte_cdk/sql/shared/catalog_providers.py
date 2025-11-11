# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, final

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._util.name_normalizers import LowerCaseNormalizer

if TYPE_CHECKING:
    from airbyte_cdk.models import ConfiguredAirbyteStream


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
    def validate_catalog(catalog: ConfiguredAirbyteCatalog) -> Any:
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
            raise exc.AirbyteInternalError(
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
            raise exc.AirbyteInternalError(
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
        return cast(dict[str, Any], self.get_configured_stream_info(stream_name).stream.json_schema)

    def get_stream_properties(
        self,
        stream_name: str,
    ) -> dict[str, dict[str, Any]]:
        """Return the names of the top-level properties for the given stream."""
        return cast(dict[str, Any], self.get_stream_json_schema(stream_name)["properties"])

    def get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str] | None:
        """Return the primary key column names for the given stream.

        We return `source_defined_primary_key` if set, or `primary_key` otherwise. If both are set,
        we assume they should not should differ, since Airbyte data integrity constraints do not
        permit overruling a source's pre-defined primary keys. If neither is set, we return `None`.

        Returns:
            A list of column names that constitute the primary key, or None if no primary key is defined.
        """
        configured_stream = self.get_configured_stream_info(stream_name)
        pks = configured_stream.stream.source_defined_primary_key or configured_stream.primary_key

        if not pks:
            return None

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
