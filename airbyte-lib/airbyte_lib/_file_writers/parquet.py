# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A Parquet cache implementation."""
from __future__ import annotations

from pathlib import Path
from typing import cast

import pyarrow as pa
import ulid
from overrides import overrides
from pyarrow import parquet

from airbyte_lib import exceptions as exc
from airbyte_lib._file_writers.base import (
    FileWriterBase,
    FileWriterBatchHandle,
    FileWriterConfigBase,
)
from airbyte_lib._util.text_util import lower_case_set


class ParquetWriterConfig(FileWriterConfigBase):
    """Configuration for the Snowflake cache."""

    # Inherits `cache_dir` from base class


class ParquetWriter(FileWriterBase):
    """A Parquet cache implementation."""

    config_class = ParquetWriterConfig

    def get_new_cache_file_path(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> Path:
        """Return a new cache file path for the given stream."""
        batch_id = batch_id or str(ulid.ULID())
        config: ParquetWriterConfig = cast(ParquetWriterConfig, self.config)
        target_dir = Path(config.cache_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / f"{stream_name}_{batch_id}.parquet"

    def _get_missing_columns(
        self,
        stream_name: str,
        record_batch: pa.Table,
    ) -> list[str]:
        """Return a list of columns that are missing in the batch.

        The comparison is based on a case-insensitive comparison of the column names.
        """
        if not self._catalog_manager:
            raise exc.AirbyteLibInternalError(message="Catalog manager should exist but does not.")
        stream = self._catalog_manager.get_stream_config(stream_name)
        stream_property_names = stream.stream.json_schema["properties"].keys()
        return [
            col
            for col in stream_property_names
            if col.lower() not in lower_case_set(record_batch.schema.names)
        ]

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table,
    ) -> FileWriterBatchHandle:
        """Process a record batch.

        Return the path to the cache file.
        """
        _ = batch_id  # unused
        output_file_path = self.get_new_cache_file_path(stream_name)

        missing_columns = self._get_missing_columns(stream_name, record_batch)
        if missing_columns:
            # We need to append columns with the missing column name(s) and a null type
            null_array = cast(pa.Array, pa.array([None] * len(record_batch), type=pa.null()))
            for col in missing_columns:
                record_batch = record_batch.append_column(col, null_array)

        with parquet.ParquetWriter(output_file_path, schema=record_batch.schema) as writer:
            writer.write_table(record_batch)

        batch_handle = FileWriterBatchHandle()
        batch_handle.files.append(output_file_path)
        return batch_handle
