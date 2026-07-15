# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Shared fixtures: an in-process DuckDB-backed processor with a configurable stream.

These tests exercise the real SQL path against a local DuckDB file, which is
the same engine code path used for `md:` targets.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider

from destination_motherduck.processors.duckdb import DuckDBConfig, DuckDBSqlProcessor

STREAM = "users"


def make_processor(
    tmp_path: Path,
    *,
    cursor_field: list[str] | None = None,
    with_cdc_column: bool = False,
) -> DuckDBSqlProcessor:
    properties = {
        "id": {"type": "integer"},
        "updated_at": {"type": "string", "format": "date-time"},
        "val": {"type": "string"},
    }
    if with_cdc_column:
        properties["_ab_cdc_deleted_at"] = {"type": "string", "format": "date-time"}

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=STREAM,
                    json_schema={"type": "object", "properties": properties},
                    supported_sync_modes=[SyncMode.incremental],
                    source_defined_primary_key=[["id"]],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                cursor_field=cursor_field,
                primary_key=[["id"]],
            )
        ]
    )
    config = DuckDBConfig(db_path=str(tmp_path / "test.duckdb"), schema_name="main")
    return DuckDBSqlProcessor(sql_config=config, catalog_provider=CatalogProvider(catalog))


@pytest.fixture
def processor(tmp_path: Path) -> DuckDBSqlProcessor:
    return make_processor(tmp_path, cursor_field=["updated_at"])


def write_batch(
    processor: DuckDBSqlProcessor,
    rows: list[dict],
    *,
    sync_mode: DestinationSyncMode = DestinationSyncMode.append_dedup,
) -> None:
    """Push rows through the real write path (buffer -> temp table -> dedup -> merge)."""
    import json
    import uuid
    from collections import defaultdict

    columns = list(processor._get_sql_column_definitions(STREAM))
    buffer: dict = {STREAM: defaultdict(list)}
    for row in rows:
        for col in columns:
            if col == "_airbyte_raw_id":
                buffer[STREAM][col].append(str(uuid.uuid4()))
            elif col == "_airbyte_meta":
                buffer[STREAM][col].append(json.dumps({}))
            else:
                buffer[STREAM][col].append(row.get(col))
    processor.prepare_stream_table(STREAM, sync_mode)
    processor.write_stream_data_from_buffer(buffer, STREAM, sync_mode)


def read_final(processor: DuckDBSqlProcessor) -> list[tuple]:
    return sorted(
        processor._execute_sql(f"SELECT id, updated_at, val FROM main.{STREAM}"),
        key=lambda r: r[0],
    )
