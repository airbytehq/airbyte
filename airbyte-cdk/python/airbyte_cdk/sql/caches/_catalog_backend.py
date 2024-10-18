# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Catalog backend implementation.

Catalog backend is responsible for storing and retrieving the stream catalog metadata to a durable
storage medium, such as an internal SQL table. It provides methods to register a source and its
streams in the cache, and to get catalog providers.
"""

from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import Session, declarative_base

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)

from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider


if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


STREAMS_TABLE_NAME = "_airbyte_streams"

SqlAlchemyModel = declarative_base()
"""A base class to use for SQLAlchemy ORM models."""


class CachedStream(SqlAlchemyModel):  # type: ignore[valid-type,misc]
    """A SQLAlchemy ORM model to store stream catalog metadata."""

    __tablename__ = STREAMS_TABLE_NAME

    stream_name = Column(String)
    source_name = Column(String)
    table_name = Column(String, primary_key=True)
    catalog_metadata = Column(String)


class CatalogBackendBase(abc.ABC):
    """A class to manage the stream catalog of data synced to a cache.

    This includes:
    - What streams exist and to what tables they map
    - The JSON schema for each stream
    """

    # Abstract implementations

    @abc.abstractmethod
    def _save_catalog_info(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        """Serialize the incoming catalog information to storage.

        Raises:
            NotImplementedError: If the catalog is static or the catalog manager is read only.
        """
        ...

    # Generic implementations

    @property
    @abc.abstractmethod
    def stream_names(self) -> list[str]:
        """Return the names of all known streams in the catalog backend."""
        ...

    @abc.abstractmethod
    def register_source(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        """Register a source and its streams in the cache."""
        ...

    @abc.abstractmethod
    def get_full_catalog_provider(self) -> CatalogProvider:
        """Return a catalog provider with the full catalog."""
        ...

    @abc.abstractmethod
    def get_source_catalog_provider(self, source_name: str) -> CatalogProvider:
        """Return a catalog provider filtered for a single source."""
        ...


class SqlCatalogBackend(CatalogBackendBase):
    """A class to manage the stream catalog of data synced to a cache.

    This includes:
    - What streams exist and to what tables they map
    - The JSON schema for each stream.
    """

    def __init__(
        self,
        engine: Engine,
        table_prefix: str,
    ) -> None:
        self._engine: Engine = engine
        self._table_prefix = table_prefix
        self._ensure_internal_tables()
        self._full_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog(
            streams=self._fetch_streams_info(
                source_name=None,
                table_prefix=self._table_prefix,
            )
        )
        self._source_catalogs: dict[str, CatalogProvider] = {}

    def _ensure_internal_tables(self) -> None:
        engine = self._engine
        SqlAlchemyModel.metadata.create_all(engine)  # type: ignore[attr-defined]

    def register_source(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        """Register a source and its streams in the cache."""
        # First, go ahead and serialize the incoming catalog information to SQL table storage
        self._save_catalog_info(
            source_name=source_name,
            incoming_source_catalog=incoming_source_catalog,
            incoming_stream_names=incoming_stream_names,
        )

        # Now update the in-memory catalog
        unchanged_streams: list[ConfiguredAirbyteStream] = [
            stream for stream in self._full_catalog.streams if stream.stream.name not in incoming_stream_names
        ]
        new_streams: list[ConfiguredAirbyteStream] = [
            stream for stream in incoming_source_catalog.streams if stream.stream.name in incoming_stream_names
        ]
        # We update the existing catalog in place, rather than creating a new one.
        # This is so that any CatalogProvider references to the catalog will see the updated
        # streams.
        self._full_catalog.streams = unchanged_streams + new_streams

        # Repeat the process for the source-specific catalog cache
        if source_name in self._source_catalogs:
            source_streams = self._source_catalogs[source_name].configured_catalog.streams
            # Now use the same process to update the source-specific catalog if it exists
            unchanged_streams = [stream for stream in source_streams if stream.stream.name not in incoming_stream_names]
            new_streams = [stream for stream in incoming_source_catalog.streams if stream.stream.name in incoming_stream_names]
            self._source_catalogs[source_name].configured_catalog.streams = new_streams + unchanged_streams

    def _save_catalog_info(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        self._ensure_internal_tables()
        engine = self._engine
        with Session(engine) as session:
            # Delete and replace existing stream entries from the catalog cache
            table_name_entries_to_delete = [self._table_prefix + incoming_stream_name for incoming_stream_name in incoming_stream_names]
            result = session.query(CachedStream).filter(CachedStream.table_name.in_(table_name_entries_to_delete)).delete()
            _ = result
            session.commit()
            insert_streams = [
                CachedStream(
                    source_name=source_name,
                    stream_name=stream.stream.name,
                    table_name=self._table_prefix + stream.stream.name,
                    catalog_metadata=json.dumps(stream.stream.json_schema),
                )
                for stream in incoming_source_catalog.streams
            ]
            session.add_all(insert_streams)
            session.commit()

    def _fetch_streams_info(
        self,
        *,
        source_name: str | None = None,
        table_prefix: str | None = None,
    ) -> list[ConfiguredAirbyteStream]:
        """Fetch the streams information from the cache.

        The `source_name` and `table_prefix` args are optional filters.
        """
        engine = self._engine
        with Session(engine) as session:
            # load all the streams
            streams: list[CachedStream] = session.query(CachedStream).all()

        if not streams:
            # no streams means the cache is pristine
            return []

        # load the catalog
        return [
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream.stream_name,
                    json_schema=json.loads(stream.catalog_metadata),  # type: ignore[arg-type]
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
            for stream in streams
            if (source_name is None or stream.source_name == source_name)
            # only load the streams where the table name matches what
            # the current cache would generate
            and (table_prefix is None or stream.table_name == table_prefix + stream.stream_name)
        ]

    @property
    def stream_names(self) -> list[str]:
        return [stream.stream.name for stream in self._full_catalog.streams]

    def get_full_catalog_provider(
        self,
    ) -> CatalogProvider:
        """Return a catalog provider with the full catalog across all sources."""
        return CatalogProvider(configured_catalog=self._full_catalog)

    def get_source_catalog_provider(
        self,
        source_name: str,
    ) -> CatalogProvider:
        if source_name not in self._source_catalogs:
            self._source_catalogs[source_name] = CatalogProvider(
                configured_catalog=ConfiguredAirbyteCatalog(
                    streams=self._fetch_streams_info(
                        source_name=source_name,
                        table_prefix=self._table_prefix,
                    )
                )
            )

        return self._source_catalogs[source_name]
