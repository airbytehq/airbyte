# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
from pathlib import Path

from conftest import STREAM, make_processor, read_final, write_batch


def _row(id_, cursor, val, extracted):
    return {"id": id_, "updated_at": cursor, "val": val, "_airbyte_extracted_at": extracted}


def test_late_backfill_does_not_overwrite_newer_record(tmp_path: Path) -> None:
    """A batch extracted later but carrying an older cursor must lose."""
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, "2026-01-02T00:00:00", "v2", "2026-01-02T00:00:00")])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "v1-late", "2026-01-03T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "v2")]


def test_newer_cursor_wins(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "v1", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-02T00:00:00", "v2", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "v2")]


def test_equal_cursor_defers_to_extraction_time(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "first", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "replayed", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "replayed")]


def test_null_cursor_loses_to_populated_cursor(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "keep", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, None, "null-cursor", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "keep")]


def test_populated_cursor_beats_null_cursor(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, None, "null-cursor", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-02T00:00:00", "wins", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "wins")]


def test_intra_batch_dedup_orders_by_cursor(tmp_path: Path) -> None:
    """Within a batch, the row with the newest cursor survives, not the last-extracted."""
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(
        p,
        [
            _row(1, "2026-01-02T00:00:00", "newest-cursor", "2026-01-01T00:00:00"),
            _row(1, "2026-01-01T00:00:00", "late-extract", "2026-01-05T00:00:00"),
        ],
    )
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "newest-cursor")]


def test_both_null_cursors_defer_to_extraction_time_stale_loses(tmp_path: Path) -> None:
    """Regression: with both cursors NULL, an older-extracted batch must not overwrite."""
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, None, "keep", "2026-01-02T00:00:00")])
    write_batch(p, [_row(1, None, "stale-replay", "2026-01-01T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "keep")]


def test_both_null_cursors_defer_to_extraction_time_newer_wins(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"])
    write_batch(p, [_row(1, None, "first", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, None, "newer-extract", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "newer-extract")]


def test_no_cursor_stream_falls_back_to_extracted_at(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=None)
    write_batch(p, [_row(1, "2026-01-05T00:00:00", "first", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "latest-extract", "2026-01-02T00:00:00")])
    assert [(r[0], r[2]) for r in read_final(p)] == [(1, "latest-extract")]
