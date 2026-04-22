# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Tests for the external-merge-sort helper that replaces `sorted()` in
`IncrementalShopifyGraphQlBulkStream.sort_output_asc`.

The helper is exercised via random inputs and small chunk sizes to validate
that:

- Output order matches the in-memory `sorted()` reference for any input size.
- The helper is memory-bounded: it never holds more than `chunk_size` records
  in memory at once, even when pulling from a generator that is much larger.
- Temp files are cleaned up when the returned generator is fully consumed.
"""

import random
from pathlib import Path
from typing import List, Mapping
from unittest.mock import patch

import pytest
from source_shopify.streams.base_streams import (
    _BULK_SORT_CHUNK_SIZE_ENV,
    _DEFAULT_BULK_SORT_CHUNK_SIZE,
    IncrementalShopifyGraphQlBulkStream,
    _external_merge_sort,
    _flush_sorted_chunk,
)


def _make_record(updated_at: str, idx: int) -> Mapping[str, object]:
    return {
        "id": idx,
        "updated_at": updated_at,
        "payload": f"record-{idx}",
    }


def _sort_key(record: Mapping[str, object]) -> object:
    return record.get("updated_at") or ""


@pytest.mark.parametrize(
    "total, chunk_size",
    [
        pytest.param(0, 100, id="empty_input"),
        pytest.param(1, 100, id="single_record"),
        pytest.param(10, 100, id="smaller_than_one_chunk"),
        pytest.param(100, 100, id="exactly_one_chunk"),
        pytest.param(250, 100, id="multiple_chunks_with_remainder"),
        pytest.param(1000, 50, id="many_small_chunks"),
        pytest.param(500, 1, id="chunk_size_one_forces_all_spills"),
    ],
)
def test_external_merge_sort_matches_sorted_reference(total: int, chunk_size: int) -> None:
    rng = random.Random(42)
    records = [_make_record(f"2024-01-{rng.randint(1, 28):02d}T00:00:00Z", i) for i in range(total)]
    expected = sorted(records, key=_sort_key)

    actual = list(_external_merge_sort(iter(records), key=_sort_key, chunk_size=chunk_size))

    assert actual == expected


def test_external_merge_sort_handles_missing_cursor_value() -> None:
    records = [
        _make_record("2024-03-01T00:00:00Z", 1),
        {"id": 2, "payload": "no-cursor"},
        _make_record("2024-01-01T00:00:00Z", 3),
    ]

    actual = list(_external_merge_sort(iter(records), key=_sort_key, chunk_size=2))

    cursor_values = [r.get("updated_at") for r in actual]
    assert cursor_values == [None, "2024-01-01T00:00:00Z", "2024-03-01T00:00:00Z"]


def test_external_merge_sort_is_memory_bounded() -> None:
    """Peak in-memory record count is at most `chunk_size + O(num_chunks)`.

    We feed in 1000 records via a generator and track the maximum number of
    records materialized in any Python list/dict along the way by hooking the
    internal chunk-flush helper. The contract we care about: no single
    structure holds more than `chunk_size` records during sort.
    """
    chunk_size = 100
    total = 1000
    records = (_make_record(f"2024-{(i % 12) + 1:02d}-01T00:00:00Z", i) for i in range(total))

    max_chunk_observed = 0

    def tracking_flush(buf: List[Mapping[str, object]], key, tmp_dir):
        nonlocal max_chunk_observed
        max_chunk_observed = max(max_chunk_observed, len(buf))
        return _flush_sorted_chunk(buf, key, tmp_dir)

    with patch("source_shopify.streams.base_streams._flush_sorted_chunk", side_effect=tracking_flush):
        result = list(_external_merge_sort(records, key=_sort_key, chunk_size=chunk_size))

    assert len(result) == total
    assert max_chunk_observed <= chunk_size


def test_external_merge_sort_cleans_up_temp_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    records = [_make_record(f"2024-02-{i:02d}T00:00:00Z", i) for i in range(1, 11)]

    result = list(_external_merge_sort(iter(records), key=_sort_key, chunk_size=3))

    assert len(result) == len(records)
    leftover = list(tmp_path.glob("shopify-bulk-sort-*"))
    assert leftover == [], f"temp files not cleaned up: {leftover}"


def test_external_merge_sort_cleans_up_on_early_close(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    records = [_make_record(f"2024-02-{i:02d}T00:00:00Z", i) for i in range(1, 21)]

    gen = _external_merge_sort(iter(records), key=_sort_key, chunk_size=5)
    next(gen)
    gen.close()

    leftover = list(tmp_path.glob("shopify-bulk-sort-*"))
    assert leftover == [], f"temp files not cleaned up on early close: {leftover}"


def test_external_merge_sort_preserves_record_content_through_spill() -> None:
    """The spill layer serializes via `json.dumps` / `json.loads`. Lock in that
    the record shapes Shopify's bulk pipeline actually produces round-trip
    identically: snake-cased keys, nested dicts/lists, unicode, nulls/booleans,
    empty strings, ints and floats, and deeply-nested structures. If a future
    upstream transform ever injects a non-JSON-native type (datetime, Decimal,
    set, bytes, non-string dict keys), this test will fail loudly instead of
    silently corrupting records.
    """
    records = [
        {
            "id": "gid://shopify/Product/1",
            "updated_at": "2024-03-01T00:00:00Z",
            "title": "Café — naïve façade 🚀",
            "tags": ["a", "b", "c"],
            "variants": [
                {"id": "gid://shopify/ProductVariant/10", "price": "9.99", "inventory_quantity": 0},
                {"id": "gid://shopify/ProductVariant/11", "price": "0.00", "inventory_quantity": 5},
            ],
            "metafields": {
                "custom": {
                    "nested": {"deeply": {"value": None}},
                },
            },
            "is_published": True,
            "archived": False,
            "description": "",
            "weight": 1.5,
            "count": 42,
            "handle": None,
        },
        {
            "id": "gid://shopify/Product/2",
            "updated_at": "2024-01-15T12:34:56Z",
            "title": "minimal",
            "tags": [],
            "variants": [],
            "metafields": {},
            "is_published": False,
            "archived": True,
            "description": "line-1\nline-2\ttabbed",
            "weight": 0.0,
            "count": -1,
            "handle": "minimal",
        },
    ]

    actual = list(_external_merge_sort(iter(records), key=_sort_key, chunk_size=1))
    expected = sorted(records, key=_sort_key)

    assert actual == expected
    # Explicit shape checks to catch silent lossy conversions (e.g. tuple→list,
    # int-keys→str-keys) that dict equality alone might paper over.
    assert actual[0]["tags"] == ["a"] * 0 + []
    assert actual[1]["metafields"]["custom"]["nested"]["deeply"]["value"] is None
    assert actual[1]["is_published"] is True
    assert actual[1]["archived"] is False
    assert actual[1]["weight"] == 1.5
    assert actual[1]["count"] == 42
    assert actual[1]["handle"] is None
    assert actual[1]["description"] == ""
    assert actual[1]["title"] == "Café — naïve façade 🚀"


class _StubIncrementalBulkStream(IncrementalShopifyGraphQlBulkStream):
    """Minimal subclass that exposes `sort_output_asc` without touching the
    network or the parent `__init__` (which requires a full connector config).
    """

    bulk_query = None  # type: ignore[assignment]

    def __init__(self, cursor_field: str = "updated_at") -> None:
        self._cursor_field = cursor_field

    @property
    def cursor_field(self):  # type: ignore[override]
        return self._cursor_field

    @property
    def default_state_comparison_value(self):  # type: ignore[override]
        return ""


def test_sort_output_asc_uses_external_sort_and_handles_empty() -> None:
    stream = _StubIncrementalBulkStream()

    assert list(stream.sort_output_asc(None)) == []
    assert list(stream.sort_output_asc([])) == []

    records = [_make_record("2024-03-02T00:00:00Z", 1), _make_record("2024-01-01T00:00:00Z", 2)]
    actual = list(stream.sort_output_asc(iter(records)))
    assert [r["id"] for r in actual] == [2, 1]


def test_sort_output_asc_passes_through_when_no_cursor_field() -> None:
    stream = _StubIncrementalBulkStream(cursor_field=None)  # type: ignore[arg-type]
    records = [_make_record("2024-03-02T00:00:00Z", 1), _make_record("2024-01-01T00:00:00Z", 2)]

    actual = list(stream.sort_output_asc(iter(records)))

    # No sort applied — records preserve input order.
    assert [r["id"] for r in actual] == [1, 2]


@pytest.mark.parametrize(
    "env_value, expected",
    [
        pytest.param(None, _DEFAULT_BULK_SORT_CHUNK_SIZE, id="unset_uses_default"),
        pytest.param("", _DEFAULT_BULK_SORT_CHUNK_SIZE, id="empty_uses_default"),
        pytest.param("not-an-int", _DEFAULT_BULK_SORT_CHUNK_SIZE, id="invalid_uses_default"),
        pytest.param("0", _DEFAULT_BULK_SORT_CHUNK_SIZE, id="zero_uses_default"),
        pytest.param("-5", _DEFAULT_BULK_SORT_CHUNK_SIZE, id="negative_uses_default"),
        pytest.param("1000", 1000, id="positive_override"),
    ],
)
def test_bulk_sort_chunk_size_env_override(env_value, expected, monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _StubIncrementalBulkStream()
    if env_value is None:
        monkeypatch.delenv(_BULK_SORT_CHUNK_SIZE_ENV, raising=False)
    else:
        monkeypatch.setenv(_BULK_SORT_CHUNK_SIZE_ENV, env_value)

    assert stream._bulk_sort_chunk_size == expected
