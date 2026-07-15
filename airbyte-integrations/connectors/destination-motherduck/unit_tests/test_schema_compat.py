# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
from pathlib import Path

from conftest import STREAM, make_processor

from airbyte_cdk.models import DestinationSyncMode


def test_schema_compat_check_runs_without_reflection(tmp_path: Path) -> None:
    """Regression: CDK reflection queries pg_catalog.pg_collation, absent in DuckDB 1.4.x."""
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    processor.prepare_stream_table(STREAM, DestinationSyncMode.append_dedup)
    # idempotent on an existing, complete table
    processor.prepare_stream_table(STREAM, DestinationSyncMode.append_dedup)


def test_schema_compat_adds_missing_column(tmp_path: Path) -> None:
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    processor._ensure_schema_exists()
    processor._execute_sql(f"CREATE TABLE main.{STREAM} (id BIGINT)")
    processor._ensure_compatible_table_schema(stream_name=STREAM, table_name=STREAM)
    columns = {
        row[0]
        for row in processor._execute_sql(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = '{STREAM}'"
        )
    }
    assert {"id", "updated_at", "val", "_airbyte_extracted_at"} <= columns


def test_schema_compat_is_case_insensitive(tmp_path: Path) -> None:
    """A table column differing from the stream column only by case must not be re-added."""
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    processor._ensure_schema_exists()
    schema = processor.sql_config.schema_name
    processor._execute_sql(f'CREATE TABLE {schema}.{STREAM} ("ID" BIGINT)')
    processor._ensure_compatible_table_schema(stream_name=STREAM, table_name=STREAM)
    id_columns = [
        row[0]
        for row in processor._execute_sql(
            f"SELECT column_name FROM information_schema.columns"
            f" WHERE table_schema = '{schema}' AND table_name = '{STREAM}' AND lower(column_name) = 'id'"
        )
    ]
    assert id_columns == ["ID"]
