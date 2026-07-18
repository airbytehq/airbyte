# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Shared fixtures: an in-process DuckDB-backed processor with a configurable stream.

These tests exercise the real SQL path against a local DuckDB file, which is
the same engine code path used for `md:` targets.
"""

from __future__ import annotations

import json
import os
import uuid
import warnings
from collections import defaultdict
from pathlib import Path

import pytest
from destination_motherduck.processors.duckdb import DuckDBConfig, DuckDBSqlProcessor
from destination_motherduck.processors.motherduck import MotherDuckConfig, MotherDuckSqlProcessor
from sqlalchemy import text

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider


STREAM = "users"

# Set MOTHERDUCK_API_KEY (and optionally MOTHERDUCK_TEST_DB, default "md:airbyte_test")
# to run the identical suite against a live MotherDuck database instead of a
# local file. Each pytest session writes to its own schema so runs cannot
# collide; schemas are dropped at session teardown, but a killed run can leave
# test_* schemas behind in the test database.
_MD_API_KEY = os.environ.get("MOTHERDUCK_API_KEY")
_MD_TEST_DB = os.environ.get("MOTHERDUCK_TEST_DB", "airbyte_test")
_SESSION_SCHEMA = f"test_{uuid.uuid4().hex[:8]}"
_MD_SCHEMAS_CREATED: list[str] = []


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
    if _MD_API_KEY:
        schema_name = f"{_SESSION_SCHEMA}_{tmp_path.name}"
        _MD_SCHEMAS_CREATED.append(schema_name)
        config = MotherDuckConfig(
            database=_MD_TEST_DB,
            api_key=_MD_API_KEY,
            schema_name=schema_name,
        )
        return MotherDuckSqlProcessor(sql_config=config, catalog_provider=CatalogProvider(catalog))
    config = DuckDBConfig(db_path=str(tmp_path / "test.duckdb"), schema_name="main")
    return DuckDBSqlProcessor(sql_config=config, catalog_provider=CatalogProvider(catalog))


@pytest.fixture
def processor(tmp_path: Path) -> DuckDBSqlProcessor:
    return make_processor(tmp_path, cursor_field=["updated_at"])


@pytest.fixture(scope="session", autouse=True)
def _drop_motherduck_schemas():
    """Best-effort cleanup: drop every MotherDuck schema this session created."""
    yield
    if not (_MD_API_KEY and _MD_SCHEMAS_CREATED):
        return
    # Reuse the connector's own engine config: a raw duckdb.connect() with different
    # settings than the engines the tests opened is rejected by MotherDuck.
    config = MotherDuckConfig(database=_MD_TEST_DB, api_key=_MD_API_KEY, schema_name="main")
    try:
        with config.get_sql_engine().begin() as conn:
            for schema in _MD_SCHEMAS_CREATED:
                try:
                    conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
                except Exception as exc:
                    warnings.warn(f"Could not drop test schema {schema}: {exc}")
    except Exception as exc:
        warnings.warn(f"Could not connect to MotherDuck to drop test schemas: {exc}")


def write_batch(
    processor: DuckDBSqlProcessor,
    rows: list[dict],
    *,
    sync_mode: DestinationSyncMode = DestinationSyncMode.append_dedup,
) -> None:
    """Push rows through the real write path (buffer -> temp table -> dedup -> merge)."""
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
    schema = processor.sql_config.schema_name
    return sorted(
        processor._execute_sql(f"SELECT id, updated_at, val FROM {schema}.{STREAM}"),
        key=lambda r: r[0],
    )
