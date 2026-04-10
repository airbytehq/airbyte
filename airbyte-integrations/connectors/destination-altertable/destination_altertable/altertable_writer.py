# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import altertable_flightsql
import pyarrow as pa
from altertable_flightsql.client import IngestIncrementalOptions, IngestTableMode

from airbyte_cdk.models import (
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
)

from .type_conversion import convert_to_arrow


# Maximum GRPC message size is 512MB. We use 400MB as a safety margin because
# we only have a message size average.
MAX_BATCH_SIZE = 400 * 1024 * 1024


@dataclass(frozen=True)
class AirbyteStream:
    name: str
    properties: dict[str, Any]
    sync_mode: DestinationSyncMode
    primary_key: list[str] = field(default_factory=list)
    cursor_field: list[str] = field(default_factory=list)


class AltertableWriter:
    def __init__(self, config: Dict[str, Any]):
        self.client = altertable_flightsql.Client(
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            tls=config.get("tls", True),
            catalog=config.get("catalog"),
            schema=config.get("schema"),
        )

        self.config = config
        self.buffer = defaultdict(list)
        self.streams: Dict[str, AirbyteStream] = {}
        self._replaced_streams: set[str] = set()

    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close client"""
        self.close()
        return False

    def close(self):
        """Close the Flight client connection"""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass  # Ignore errors on close

    def set_streams(self, catalog: ConfiguredAirbyteCatalog):
        self.streams.update(
            {
                stream.stream.name: AirbyteStream(
                    name=stream.stream.name,
                    properties=stream.stream.json_schema["properties"],
                    sync_mode=stream.destination_sync_mode,
                    primary_key=self._get_primary_key(stream.primary_key or stream.stream.source_defined_primary_key),
                    cursor_field=stream.cursor_field or stream.stream.source_defined_cursor or [],
                )
                for stream in catalog.streams
            }
        )

    def test_connection(self):
        stream = self.client.query("SELECT 1")
        stream.read_all()

    def buffer_record(self, record: AirbyteRecordMessage):
        self.buffer[record.stream].append(record)

    def _get_primary_key(self, primary_key: list[list[str]] | None) -> list[str]:
        if primary_key is None:
            return []
        if any(len(pkey) > 1 for pkey in primary_key):
            raise NotImplementedError("Nested primary keys are not supported yet")
        return [pkey[0] for pkey in primary_key]

    def _convert_records_to_pyarrow_table(self, stream: str, records: list[AirbyteRecordMessage]) -> pa.Table:
        properties = self.streams[stream].properties

        fields = []
        converted_rows = [{} for _ in records]

        for field_name, prop in properties.items():
            # Get the first non-null value to determine type (or use None)
            sample_value = next(
                (r.data.get(field_name) for r in records if r.data.get(field_name) is not None),
                None,
            )
            pa_type, _ = convert_to_arrow(sample_value, prop)
            fields.append((field_name, pa_type))

            # Convert all values for this field
            for i, record in enumerate(records):
                _, converted = convert_to_arrow(record.data.get(field_name), prop)
                converted_rows[i][field_name] = converted

        schema = pa.schema(fields)
        return pa.Table.from_pylist(converted_rows, schema=schema)

    def _estimate_rows_per_batch(self, table: pa.Table) -> int:
        if rows_per_batch := self.config.get("rows_per_batch"):
            return rows_per_batch

        # Split table into batches to avoid gRPC message size limits (512MB default)
        # Use memory size to determine batch boundaries (400MB per batch to stay safely under 512MB limit)
        total_size = table.get_total_buffer_size()
        if total_size > MAX_BATCH_SIZE:
            return max(1, int(len(table) * MAX_BATCH_SIZE / total_size))
        else:
            return len(table)

    def _get_incremental_options(self, stream_config: AirbyteStream) -> Optional[IngestIncrementalOptions]:
        if stream_config.sync_mode not in (
            DestinationSyncMode.append_dedup,
            DestinationSyncMode.update,
        ):
            return None

        if not stream_config.primary_key:
            raise ValueError(f"Stream {stream_config.name} has no primary key but {stream_config.sync_mode} requires one")

        return IngestIncrementalOptions(
            primary_key=stream_config.primary_key,
            cursor_field=stream_config.cursor_field,
        )

    def _get_ingest_mode(self, stream: str, sync_mode: DestinationSyncMode) -> IngestTableMode:
        if sync_mode != DestinationSyncMode.overwrite:
            return IngestTableMode.CREATE_APPEND
        if stream in self._replaced_streams:
            return IngestTableMode.CREATE_APPEND
        return IngestTableMode.REPLACE

    def flush(self):
        for stream, records in self.buffer.items():
            if not records:
                continue

            stream_config = self.streams[stream]
            table = self._convert_records_to_pyarrow_table(stream, records)
            mode = self._get_ingest_mode(stream, stream_config.sync_mode)

            with self.client.ingest(
                table_name=stream,
                schema=table.schema,
                schema_name=self.config.get("schema", ""),
                catalog_name=self.config.get("catalog", ""),
                mode=mode,
                incremental_options=self._get_incremental_options(stream_config),
            ) as writer:
                estimated_rows_per_batch = self._estimate_rows_per_batch(table)
                batches = table.to_batches(max_chunksize=estimated_rows_per_batch)

                for batch in batches:
                    writer.write_batch(batch)

            if mode == IngestTableMode.REPLACE:
                self._replaced_streams.add(stream)

        self.buffer.clear()
