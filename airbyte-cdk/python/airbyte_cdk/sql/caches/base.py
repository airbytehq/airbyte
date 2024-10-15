# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""SQL Cache implementation."""

from __future__ import annotations

from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, final

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
from pydantic import Field, PrivateAttr
from sqlalchemy import text

from airbyte_cdk.models import ConfiguredAirbyteCatalog

from airbyte_cdk.sql import constants
from airbyte_cdk.sql._writers.base import AirbyteWriterInterface
from airbyte_cdk.sql.caches._catalog_backend import CatalogBackendBase, SqlCatalogBackend
from airbyte_cdk.sql.caches._state_backend import SqlStateBackend
from airbyte_cdk.sql.constants import DEFAULT_ARROW_MAX_CHUNK_SIZE, TEMP_FILE_CLEANUP
from airbyte_cdk.sql.datasets._sql import CachedDataset
from airbyte_cdk.sql.catalog_providers import CatalogProvider
from airbyte_cdk.sql.sql_processor import (
    SqlConfig,
    SqlProcessorBase,
)
from airbyte_cdk.sql.state_writers import StdOutStateWriter


if TYPE_CHECKING:
    from collections.abc import Iterator

    from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator
    from airbyte_cdk.sql.caches._state_backend_base import StateBackendBase
    from airbyte_cdk.sql.datasets._base import DatasetBase
    from airbyte_cdk.sql.progress import ProgressTracker
    from airbyte_cdk.sql.sql_processor import SqlProcessorBase
    from airbyte_cdk.sql.state_providers import StateProviderBase
    from airbyte_cdk.sql.state_writers import StateWriterBase
    from airbyte_cdk.sql.strategies import WriteStrategy


class CacheBase(SqlConfig, AirbyteWriterInterface):
    """Base configuration for a cache.

    Caches inherit from the matching `SqlConfig` class, which provides the SQL config settings
    and basic connectivity to the SQL database.

    The cache is responsible for managing the state of the data synced to the cache, including the
    stream catalog and stream state. The cache also provides the mechanism to read and write data
    to the SQL backend specified in the `SqlConfig` class.
    """

    cache_dir: Path = Field(default=Path(constants.DEFAULT_CACHE_ROOT))
    """The directory to store the cache in."""

    cleanup: bool = TEMP_FILE_CLEANUP
    """Whether to clean up the cache after use."""

    _name: str = PrivateAttr()

    _deployed_api_root: str | None = PrivateAttr(default=None)
    _deployed_workspace_id: str | None = PrivateAttr(default=None)
    _deployed_destination_id: str | None = PrivateAttr(default=None)

    _sql_processor_class: type[SqlProcessorBase] = PrivateAttr()
    _read_processor: SqlProcessorBase = PrivateAttr()

    _catalog_backend: CatalogBackendBase = PrivateAttr()
    _state_backend: StateBackendBase = PrivateAttr()

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        """Initialize the cache and backends."""
        super().__init__(**data)

        # Create a temporary processor to do the work of ensuring the schema exists
        temp_processor = self._sql_processor_class(
            sql_config=self,
            catalog_provider=CatalogProvider(ConfiguredAirbyteCatalog(streams=[])),
            state_writer=StdOutStateWriter(),
            temp_dir=self.cache_dir,
            temp_file_cleanup=self.cleanup,
        )
        temp_processor._ensure_schema_exists()  # noqa: SLF001  # Accessing non-public member

        # Initialize the catalog and state backends
        self._catalog_backend = SqlCatalogBackend(
            engine=self.get_sql_engine(),
            table_prefix=self.table_prefix or "",
        )
        self._state_backend = SqlStateBackend(
            engine=self.get_sql_engine(),
            table_prefix=self.table_prefix or "",
        )

        # Now we can create the SQL read processor
        self._read_processor = self._sql_processor_class(
            sql_config=self,
            catalog_provider=self._catalog_backend.get_full_catalog_provider(),
            state_writer=StdOutStateWriter(),  # Shouldn't be needed for the read-only processor
            temp_dir=self.cache_dir,
            temp_file_cleanup=self.cleanup,
        )

    @property
    def config_hash(self) -> str | None:
        """Return a hash of the cache configuration.

        This is the same as the SQLConfig hash from the superclass.
        """
        return super(SqlConfig, self).config_hash

    def execute_sql(self, sql: str | list[str]) -> None:
        """Execute one or more SQL statements against the cache's SQL backend.

        If multiple SQL statements are given, they are executed in order,
        within the same transaction.

        This method is useful for creating tables, indexes, and other
        schema objects in the cache. It does not return any results and it
        automatically closes the connection after executing all statements.

        This method is not intended for querying data. For that, use the `get_records`
        method - or for a low-level interface, use the `get_sql_engine` method.

        If any of the statements fail, the transaction is canceled and an exception
        is raised. Most databases will rollback the transaction in this case.
        """
        if isinstance(sql, str):
            # Coerce to a list if a single string is given
            sql = [sql]

        with self.processor.get_sql_connection() as connection:
            for sql_statement in sql:
                connection.execute(text(sql_statement))

    @final
    @property
    def processor(self) -> SqlProcessorBase:
        """Return the SQL processor instance."""
        return self._read_processor

    def get_record_processor(
        self,
        source_name: str,
        catalog_provider: CatalogProvider,
        state_writer: StateWriterBase | None = None,
    ) -> SqlProcessorBase:
        """Return a record processor for the specified source name and catalog.

        We first register the source and its catalog with the catalog manager. Then we create a new
        SQL processor instance with (only) the given input catalog.

        For the state writer, we use a state writer which stores state in an internal SQL table.
        """
        # First register the source and catalog into durable storage. This is necessary to ensure
        # that we can later retrieve the catalog information.
        self.register_source(
            source_name=source_name,
            incoming_source_catalog=catalog_provider.configured_catalog,
            stream_names=set(catalog_provider.stream_names),
        )

        # Next create a new SQL processor instance with the given catalog - and a state writer
        # that writes state to the internal SQL table and associates with the given source name.
        return self._sql_processor_class(
            sql_config=self,
            catalog_provider=catalog_provider,
            state_writer=state_writer or self.get_state_writer(source_name=source_name),
            temp_dir=self.cache_dir,
            temp_file_cleanup=self.cleanup,
        )

    # Read methods:

    def get_records(
        self,
        stream_name: str,
    ) -> CachedDataset:
        """Uses SQLAlchemy to select all rows from the table."""
        return CachedDataset(self, stream_name)

    def get_pandas_dataframe(
        self,
        stream_name: str,
    ) -> pd.DataFrame:
        """Return a Pandas data frame with the stream's data."""
        table_name = self._read_processor.get_sql_table_name(stream_name)
        engine = self.get_sql_engine()
        return pd.read_sql_table(table_name, engine, schema=self.schema_name)

    def get_arrow_dataset(
        self,
        stream_name: str,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE,
    ) -> ds.Dataset:
        """Return an Arrow Dataset with the stream's data."""
        table_name = self._read_processor.get_sql_table_name(stream_name)
        engine = self.get_sql_engine()

        # Read the table in chunks to handle large tables which does not fits in memory
        pandas_chunks = pd.read_sql_table(
            table_name=table_name,
            con=engine,
            schema=self.schema_name,
            chunksize=max_chunk_size,
        )

        arrow_batches_list = []
        arrow_schema = None

        for pandas_chunk in pandas_chunks:
            if arrow_schema is None:
                # Initialize the schema with the first chunk
                arrow_schema = pa.Schema.from_pandas(pandas_chunk)

            # Convert each pandas chunk to an Arrow Table
            arrow_table = pa.RecordBatch.from_pandas(pandas_chunk, schema=arrow_schema)
            arrow_batches_list.append(arrow_table)

        return ds.dataset(arrow_batches_list)

    @final
    @property
    def streams(self) -> dict[str, CachedDataset]:
        """Return a temporary table name."""
        result = {}
        stream_names = set(self._catalog_backend.stream_names)

        for stream_name in stream_names:
            result[stream_name] = CachedDataset(self, stream_name)

        return result

    def get_state_provider(
        self,
        source_name: str,
        *,
        refresh: bool = True,
        destination_name: str | None = None,
    ) -> StateProviderBase:
        """Return a state provider for the specified source name."""
        return self._state_backend.get_state_provider(
            source_name=source_name,
            table_prefix=self.table_prefix or "",
            refresh=refresh,
            destination_name=destination_name,
        )

    def get_state_writer(
        self,
        source_name: str,
        destination_name: str | None = None,
    ) -> StateWriterBase:
        """Return a state writer for the specified source name.

        If syncing to the cache, `destination_name` should be `None`.
        If syncing to a destination, `destination_name` should be the destination name.
        """
        return self._state_backend.get_state_writer(
            source_name=source_name,
            destination_name=destination_name,
        )

    def register_source(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        stream_names: set[str],
    ) -> None:
        """Register the source name and catalog."""
        self._catalog_backend.register_source(
            source_name=source_name,
            incoming_source_catalog=incoming_source_catalog,
            incoming_stream_names=stream_names,
        )

    def __getitem__(self, stream: str) -> DatasetBase:
        """Return a dataset by stream name."""
        return self.streams[stream]

    def __contains__(self, stream: str) -> bool:
        """Return whether a stream is in the cache."""
        return stream in (self._catalog_backend.stream_names)

    def __iter__(  # type: ignore [override]  # Overriding Pydantic model method
        self,
    ) -> Iterator[tuple[str, Any]]:
        """Iterate over the streams in the cache."""
        return ((name, dataset) for name, dataset in self.streams.items())

    def _write_airbyte_message_stream(
        self,
        stdin: IO[str] | AirbyteMessageIterator,
        *,
        catalog_provider: CatalogProvider,
        write_strategy: WriteStrategy,
        state_writer: StateWriterBase | None = None,
        progress_tracker: ProgressTracker,
    ) -> None:
        """Read from the connector and write to the cache."""
        cache_processor = self.get_record_processor(
            source_name=self.name,
            catalog_provider=catalog_provider,
            state_writer=state_writer,
        )
        cache_processor.process_airbyte_messages(
            messages=stdin,
            write_strategy=write_strategy,
            progress_tracker=progress_tracker,
        )
        progress_tracker.log_cache_processing_complete()
