# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Verify that paginated streams use an immutable sort key to prevent
offset-based pagination from skipping records when rows are updated
concurrently during a long-running read.

Background: oncall/12026 — sorting by `updated_at` with offset-based
CursorPagination causes position-shift races when active records move
in the sort order mid-page-fetch.

Which immutable key is usable depends on what each Chargebee endpoint
accepts for `sort_by`; the expectations below record that per stream so
a regression to a mutable key fails here rather than in production.
"""

from pathlib import Path

import pytest
import yaml


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

# Every stream that paginates with offset-based CursorPagination, mapped to
# the immutable sort key its Chargebee endpoint accepts.
#
# Most endpoints accept "created_at". /invoices and /transactions do not —
# their documented sort_by attributes are "date" and "updated_at" only — so
# they use "date", which is likewise immutable. Same for /credit_notes and
# /quotes. /events sorts on "occurred_at".
_EXPECTED_SORT_BY = {
    "addon": "created_at",
    "comment": "created_at",
    "credit_note": "date",
    "customer": "created_at",
    "differential_price": "created_at",
    "event": "occurred_at",
    "hosted_page": "created_at",
    "invoice": "date",
    "item": "created_at",
    "item_family": "created_at",
    "item_price": "created_at",
    "order": "created_at",
    "payment_source": "created_at",
    "plan": "created_at",
    "promotional_credit": "created_at",
    "quote": "date",
    "subscription": "created_at",
    "transaction": "date",
    "virtual_bank_account": "created_at",
}

# Sort keys that Chargebee mutates on write. Sorting on any of these
# reintroduces oncall/12026.
_MUTABLE_SORT_KEYS = {"updated_at"}


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(_MANIFEST_PATH.read_text())


def _sort_by(manifest, stream_name):
    request_parameters = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["request_parameters"]
    return request_parameters["sort_by[asc]"]


@pytest.mark.parametrize("stream_name,expected", sorted(_EXPECTED_SORT_BY.items()), ids=sorted(_EXPECTED_SORT_BY))
def test_sort_by_uses_expected_immutable_key(manifest, stream_name, expected):
    """sort_by must be the immutable key this endpoint accepts, so pagination offsets stay stable."""
    sort_by = _sort_by(manifest, stream_name)
    assert sort_by == expected, (
        f"Stream '{stream_name}' sorts by '{sort_by}' but must sort by '{expected}' "
        f"to prevent offset-based pagination from skipping records (see oncall/12026)."
    )


def test_no_paginated_stream_sorts_by_a_mutable_key(manifest):
    """Catch-all: no stream with a sort_by may use a key Chargebee mutates, including new streams."""
    offenders = {}
    for stream_name, stream_def in manifest["definitions"]["streams"].items():
        request_parameters = (stream_def.get("retriever", {}).get("requester", {}) or {}).get("request_parameters") or {}
        sort_by = request_parameters.get("sort_by[asc]")
        if sort_by in _MUTABLE_SORT_KEYS:
            offenders[stream_name] = sort_by
    assert not offenders, (
        f"These streams sort by a mutable key and will skip records under offset pagination: {offenders}. "
        f"Use an immutable sort key accepted by the endpoint (see oncall/12026)."
    )


def test_expected_sort_by_covers_every_stream_that_sorts(manifest):
    """Guard the map itself: a new stream with a sort_by must be classified here."""
    streams_with_sort_by = {
        stream_name
        for stream_name, stream_def in manifest["definitions"]["streams"].items()
        if ((stream_def.get("retriever", {}).get("requester", {}) or {}).get("request_parameters") or {}).get("sort_by[asc]")
    }
    unclassified = streams_with_sort_by - set(_EXPECTED_SORT_BY)
    assert not unclassified, f"Streams set sort_by but are not covered by _EXPECTED_SORT_BY: {sorted(unclassified)}"
