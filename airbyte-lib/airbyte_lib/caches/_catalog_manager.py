# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A SQL Cache implementation."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from airbyte_protocol.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)

from airbyte_lib import exceptions as exc


if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

STREAMS_TABLE_NAME = "_airbytelib_streams"

Base = declarative_base()


class CachedStream(Base):  # type: ignore[valid-type,misc]
    __tablename__ = STREAMS_TABLE_NAME

    stream_name = Column(String)
    source_name = Column(String)
    table_name = Column(String, primary_key=True)
    catalog_metadata = Column(String)


class CatalogManager:
    def __init__(
        self,
        engine: Engine,
        table_name_resolver: Callable[[str], str],
    ) -> None:
        self._engine: Engine = engine
        self._table_name_resolver = table_name_resolver
        self._source_catalog: ConfiguredAirbyteCatalog | None = None
        self._load_catalog_from_internal_table()
        assert self._source_catalog is not None

    @property
    def source_catalog(self) -> ConfiguredAirbyteCatalog:
        """Return the source catalog.

        Raises:
            AirbyteLibInternalError: If the source catalog is not set.
        """
        if not self._source_catalog:
            raise exc.AirbyteLibInternalError(
                message="Source catalog should be initialized but is not.",
            )

        return self._source_catalog

    def _ensure_internal_tables(self) -> None:
        engine = self._engine
        Base.metadata.create_all(engine)

    def register_source(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        """Register a source and its streams in the cache."""
        self._update_catalog(
            incoming_source_catalog=incoming_source_catalog,
            incoming_stream_names=incoming_stream_names,
        )
        self._save_catalog_to_internal_table(
            source_name=source_name,
            incoming_source_catalog=incoming_source_catalog,
            incoming_stream_names=incoming_stream_names,
        )

    def _update_catalog(
        self,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        if not self._source_catalog:
            self._source_catalog = ConfiguredAirbyteCatalog(
                streams=[
                    stream
                    for stream in incoming_source_catalog.streams
                    if stream.stream.name in incoming_stream_names
                ],
            )
            assert len(self._source_catalog.streams) == len(incoming_stream_names)
            return

        # Keep existing streams untouched if not incoming
        unchanged_streams: list[ConfiguredAirbyteStream] = [
            stream
            for stream in self._source_catalog.streams
            if stream.stream.name not in incoming_stream_names
        ]
        new_streams: list[ConfiguredAirbyteStream] = [
            stream
            for stream in incoming_source_catalog.streams
            if stream.stream.name in incoming_stream_names
        ]
        self._source_catalog = ConfiguredAirbyteCatalog(streams=unchanged_streams + new_streams)

    def _save_catalog_to_internal_table(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        incoming_stream_names: set[str],
    ) -> None:
        self._ensure_internal_tables()
        engine = self._engine
        with Session(engine) as session:
            # Delete and replace existing stream entries from the catalog cache
            table_name_entries_to_delete = [
                self._table_name_resolver(incoming_stream_name)
                for incoming_stream_name in incoming_stream_names
            ]
            result = (
                session.query(CachedStream)
                .filter(CachedStream.table_name.in_(table_name_entries_to_delete))
                .delete()
            )
            _ = result
            session.commit()
            insert_streams = [
                CachedStream(
                    source_name=source_name,
                    stream_name=stream.stream.name,
                    table_name=self._table_name_resolver(stream.stream.name),
                    catalog_metadata=json.dumps(stream.stream.json_schema),
                )
                for stream in incoming_source_catalog.streams
            ]
            session.add_all(insert_streams)
            session.commit()

    def get_stream_config(
        self,
        stream_name: str,
    ) -> ConfiguredAirbyteStream:
        """Return the column definitions for the given stream."""
        if not self.source_catalog:
            raise exc.AirbyteLibInternalError(
                message="Cannot get stream JSON schema without a catalog.",
            )

        matching_streams: list[ConfiguredAirbyteStream] = [
            stream for stream in self.source_catalog.streams if stream.stream.name == stream_name
        ]
        if not matching_streams:
            raise exc.AirbyteStreamNotFoundError(
                stream_name=stream_name,
                context={
                    "available_streams": [
                        stream.stream.name for stream in self.source_catalog.streams
                    ],
                },
            )

        if len(matching_streams) > 1:
            raise exc.AirbyteLibInternalError(
                message="Multiple streams found with same name.",
                context={
                    "stream_name": stream_name,
                },
            )

        return matching_streams[0]

    def _load_catalog_from_internal_table(self) -> None:
        self._ensure_internal_tables()
        engine = self._engine
        with Session(engine) as session:
            # load all the streams
            streams: list[CachedStream] = session.query(CachedStream).all()
            if not streams:
                # no streams means the cache is pristine
                if not self._source_catalog:
                    self._source_catalog = ConfiguredAirbyteCatalog(streams=[])

                return

            # load the catalog
            self._source_catalog = ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream(
                            name=stream.stream_name,
                            json_schema=json.loads(stream.catalog_metadata),
                            supported_sync_modes=[SyncMode.full_refresh],
                        ),
                        sync_mode=SyncMode.full_refresh,
                        destination_sync_mode=DestinationSyncMode.append,
                    )
                    for stream in streams
                    # only load the streams where the table name matches what
                    # the current cache would generate
                    if stream.table_name == self._table_name_resolver(stream.stream_name)
                ]
            )
