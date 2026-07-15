# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
from pathlib import Path
from unittest.mock import patch

from conftest import STREAM, make_processor, read_final, write_batch

from airbyte_cdk.models import DestinationSyncMode


def test_append_dedup_uses_native_merge(tmp_path: Path) -> None:
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    with (
        patch.object(processor, "_merge_temp_table_to_final_table") as native,
        patch.object(processor, "_emulated_merge_temp_table_to_final_table") as emulated,
        patch.object(processor, "_ensure_compatible_table_schema"),
    ):
        processor._write_temp_table_to_target_table(
            stream_name=STREAM,
            temp_table_name="tmp",
            final_table_name=STREAM,
            sync_mode=DestinationSyncMode.append_dedup,
        )
    native.assert_called_once()
    emulated.assert_not_called()


def test_append_dedup_end_to_end(tmp_path: Path) -> None:
    """Two batches for the same PK leave exactly one row, reflecting the newer batch."""
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(
        processor,
        [{"id": 1, "updated_at": "2026-01-01T00:00:00", "val": "v1", "_airbyte_extracted_at": "2026-01-01T00:00:00"}],
    )
    write_batch(
        processor,
        [
            {"id": 1, "updated_at": "2026-01-02T00:00:00", "val": "v2", "_airbyte_extracted_at": "2026-01-02T00:00:00"},
            {"id": 2, "updated_at": "2026-01-02T00:00:00", "val": "other", "_airbyte_extracted_at": "2026-01-02T00:00:00"},
        ],
    )
    rows = read_final(processor)
    assert [(r[0], r[2]) for r in rows] == [(1, "v2"), (2, "other")]


def test_append_dedup_intra_batch(tmp_path: Path) -> None:
    """Duplicate PKs within one batch collapse to a single row before the merge."""
    processor = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(
        processor,
        [
            {"id": 1, "updated_at": "2026-01-01T00:00:00", "val": "old", "_airbyte_extracted_at": "2026-01-01T00:00:00"},
            {"id": 1, "updated_at": "2026-01-02T00:00:00", "val": "new", "_airbyte_extracted_at": "2026-01-02T00:00:00"},
        ],
    )
    rows = read_final(processor)
    assert len(rows) == 1
