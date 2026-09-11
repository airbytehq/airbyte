# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the disk-backed external sort used by the Shopify bulk streams.

These tests cover the behaviors that matter for the metafield OOM fix:

- parity with Python's stable `sorted()` on representative inputs
- stability for records that share a cursor value (original order preserved)
- correctness when the input is large enough to spill multiple runs to disk
- correctness on the fast path when the entire input fits in one chunk
- cleanup of spill files on normal completion, on generator close, and on
  exceptions raised from downstream consumers
"""

import os
from pathlib import Path
from typing import Any, Mapping

import pytest
from source_shopify.shopify_graphql.bulk.external_sort import (
    DEFAULT_SORT_CHUNK_SIZE,
    external_stable_sort,
)


def _cursor_key(record: Mapping[str, Any]) -> Any:
    return record.get("updated_at") or ""


def _records(values):
    # Use an incrementing id to let tests verify stable ordering.
    return [{"id": i, "updated_at": v} for i, v in enumerate(values)]


def test_matches_python_sorted_on_mixed_values():
    records = _records(
        [
            "2024-01-05T00:00:00Z",
            "2024-01-01T00:00:00Z",
            "2024-01-03T00:00:00Z",
            "2024-01-02T00:00:00Z",
            "2024-01-04T00:00:00Z",
        ]
    )

    expected = sorted(records, key=_cursor_key)
    actual = list(external_stable_sort(records, key_fn=_cursor_key))

    assert actual == expected


def test_fast_path_does_not_spill(tmp_path, monkeypatch):
    records = _records(["2024-01-02T00:00:00Z", "2024-01-01T00:00:00Z"])

    before = set(os.listdir(tmp_path))
    list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=100, tmp_dir=str(tmp_path)))
    after = set(os.listdir(tmp_path))

    assert before == after, "fast path must not create spill files"


def test_stability_on_equal_keys_across_runs():
    # Six records all with the same `updated_at`; forcing chunk_size=2 guarantees
    # the input is split into three spilled runs and then merged. The stable
    # contract is that their original ordinal order is preserved after merge.
    records = _records(["2024-01-01T00:00:00Z"] * 6)

    sorted_records = list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=2))

    assert [r["id"] for r in sorted_records] == [0, 1, 2, 3, 4, 5]


def test_multi_run_merge_matches_python_sorted():
    values = [
        "2024-01-03T00:00:00Z",
        "2024-01-01T00:00:00Z",
        "2024-01-02T00:00:00Z",
        "2024-01-01T00:00:00Z",  # duplicate cursor value
        "2024-01-04T00:00:00Z",
        "2024-01-02T00:00:00Z",  # duplicate cursor value
        "2024-01-05T00:00:00Z",
    ]
    records = _records(values)

    expected = sorted(records, key=_cursor_key)
    # chunk_size=3 forces three spilled runs + heap merge
    actual = list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=3))

    assert actual == expected
    # verify ordering for duplicate cursor values preserves input order
    assert [r["id"] for r in actual if r["updated_at"] == "2024-01-01T00:00:00Z"] == [1, 3]
    assert [r["id"] for r in actual if r["updated_at"] == "2024-01-02T00:00:00Z"] == [2, 5]


def test_handles_empty_input():
    assert list(external_stable_sort([], key_fn=_cursor_key)) == []


def test_handles_missing_cursor_values_via_fallback_key():
    records = [
        {"id": 0, "updated_at": "2024-01-02T00:00:00Z"},
        {"id": 1},
        {"id": 2, "updated_at": "2024-01-01T00:00:00Z"},
    ]

    sorted_records = list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=2))

    # Record with missing cursor value falls back to `""` and sorts first,
    # ahead of both ISO-8601 strings, matching the existing behavior.
    assert [r["id"] for r in sorted_records] == [1, 2, 0]


def test_cleans_up_spill_files_on_normal_completion(tmp_path):
    records = _records([f"2024-01-{i:02d}T00:00:00Z" for i in range(1, 11)])

    list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=3, tmp_dir=str(tmp_path)))

    remaining = [p for p in Path(tmp_path).iterdir() if p.name.startswith("shopify_bulk_sort_")]
    assert remaining == []


def test_cleans_up_spill_files_on_consumer_exception(tmp_path):
    records = _records([f"2024-01-{i:02d}T00:00:00Z" for i in range(1, 11)])

    gen = external_stable_sort(records, key_fn=_cursor_key, chunk_size=3, tmp_dir=str(tmp_path))
    next(gen)

    # Force the generator to unwind; the `finally` block should remove any
    # spill files that were created during record accumulation.
    gen.close()

    remaining = [p for p in Path(tmp_path).iterdir() if p.name.startswith("shopify_bulk_sort_")]
    assert remaining == []


def test_cleans_up_spill_files_when_record_is_not_json_serializable(tmp_path):
    # Force a chunk boundary that the sort will try to spill, then make the
    # second chunk contain an unserializable record so `json.dumps` raises
    # mid-write. The temp file that was created for that chunk must still be
    # cleaned up by the outer `finally`.
    class _NotJson:
        pass

    records = [
        {"id": 0, "updated_at": "2024-01-01T00:00:00Z"},
        {"id": 1, "updated_at": "2024-01-02T00:00:00Z"},
        {"id": 2, "updated_at": "2024-01-03T00:00:00Z", "payload": _NotJson()},
        {"id": 3, "updated_at": "2024-01-04T00:00:00Z"},
    ]

    with pytest.raises(TypeError):
        list(external_stable_sort(records, key_fn=_cursor_key, chunk_size=2, tmp_dir=str(tmp_path)))

    remaining = [p for p in Path(tmp_path).iterdir() if p.name.startswith("shopify_bulk_sort_")]
    assert remaining == []


def test_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError):
        list(external_stable_sort(_records(["a"]), key_fn=_cursor_key, chunk_size=0))


def test_default_chunk_size_is_exposed():
    # Sanity check that the public constant is a sensible positive integer.
    assert isinstance(DEFAULT_SORT_CHUNK_SIZE, int)
    assert DEFAULT_SORT_CHUNK_SIZE > 0
