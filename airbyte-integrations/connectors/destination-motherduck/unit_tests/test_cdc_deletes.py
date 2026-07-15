# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
from pathlib import Path

from conftest import STREAM, make_processor, write_batch


def _row(id_, cursor, val, extracted, deleted_at=None):
    return {
        "id": id_,
        "updated_at": cursor,
        "val": val,
        "_airbyte_extracted_at": extracted,
        "_ab_cdc_deleted_at": deleted_at,
    }


def _read_with_deleted(p) -> list[tuple]:
    """Rows as (id, val, _ab_cdc_deleted_at), ordered by id."""
    schema = p.sql_config.schema_name
    return sorted(
        p._execute_sql(f"SELECT id, val, _ab_cdc_deleted_at FROM {schema}.{STREAM}"),
        key=lambda r: r[0],
    )


def test_cdc_tombstone_soft_deletes_row(tmp_path: Path) -> None:
    """A tombstone upserts: the row remains with _ab_cdc_deleted_at set."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "live", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-02T00:00:00", None, "2026-01-02T00:00:00", deleted_at="2026-01-02T00:00:00")])
    rows = _read_with_deleted(p)
    assert len(rows) == 1
    assert rows[0][1] is None
    assert rows[0][2] is not None


def test_stale_cdc_tombstone_is_ignored(tmp_path: Path) -> None:
    """A tombstone with an older cursor than the destination row must not mark it deleted."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(1, "2026-01-03T00:00:00", "newer", "2026-01-03T00:00:00")])
    write_batch(p, [_row(1, "2026-01-01T00:00:00", None, "2026-01-04T00:00:00", deleted_at="2026-01-01T00:00:00")])
    assert _read_with_deleted(p) == [(1, "newer", None)]


def test_tombstone_for_unseen_pk_inserts_deleted_row(tmp_path: Path) -> None:
    """A tombstone for a PK the destination has never seen lands as a deleted row."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(99, "2026-01-01T00:00:00", None, "2026-01-01T00:00:00", deleted_at="2026-01-01T00:00:00")])
    rows = _read_with_deleted(p)
    assert len(rows) == 1
    assert rows[0][0] == 99
    assert rows[0][2] is not None


def test_delete_then_reinsert(tmp_path: Path) -> None:
    """A record recreated at the source after deletion is live again in the destination."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "v1", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, "2026-01-02T00:00:00", None, "2026-01-02T00:00:00", deleted_at="2026-01-02T00:00:00")])
    write_batch(p, [_row(1, "2026-01-03T00:00:00", "reborn", "2026-01-03T00:00:00")])
    assert _read_with_deleted(p) == [(1, "reborn", None)]


def test_tombstone_with_null_cursor_soft_deletes(tmp_path: Path) -> None:
    """A tombstone carrying only the PK (NULL cursor, e.g. Debezium) still marks the row deleted."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(1, "2026-01-01T00:00:00", "live", "2026-01-01T00:00:00")])
    write_batch(p, [_row(1, None, None, "2026-01-02T00:00:00", deleted_at="2026-01-02T00:00:00")])
    rows = _read_with_deleted(p)
    assert len(rows) == 1
    assert rows[0][2] is not None


def test_stale_tombstone_with_null_cursor_is_ignored(tmp_path: Path) -> None:
    """A NULL-cursor tombstone extracted before the destination row must not mark it deleted."""
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=True)
    write_batch(p, [_row(1, "2026-01-03T00:00:00", "newer", "2026-01-03T00:00:00")])
    write_batch(p, [_row(1, None, None, "2026-01-02T00:00:00", deleted_at="2026-01-02T00:00:00")])
    assert _read_with_deleted(p) == [(1, "newer", None)]


def test_non_cdc_stream_sql_has_no_tombstone_branch(tmp_path: Path) -> None:
    p = make_processor(tmp_path, cursor_field=["updated_at"], with_cdc_column=False)
    executed: list[str] = []
    original = p._execute_sql

    def capture(sql, *args, **kwargs):
        executed.append(str(sql))
        return original(sql, *args, **kwargs)

    p._execute_sql = capture
    write_batch(p, [_row_no_cdc(1)])
    merge_sql = next(s for s in executed if "MERGE INTO" in s)
    assert "_ab_cdc_deleted_at" not in merge_sql


def _row_no_cdc(id_):
    return {"id": id_, "updated_at": "2026-01-01T00:00:00", "val": "x", "_airbyte_extracted_at": "2026-01-01T00:00:00"}
