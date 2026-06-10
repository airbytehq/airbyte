# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Verify that paginated streams use an immutable sort key (created_at)
to prevent offset-based pagination from skipping records when rows
are updated concurrently during a long-running read.

Background: oncall/12026 — sorting by `updated_at` with offset-based
CursorPagination causes position-shift races when active records move
in the sort order mid-page-fetch.
"""

from pathlib import Path

import pytest
import yaml


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

# Streams that use offset-based CursorPagination with an
# updated_at[between] filter. These MUST sort by an immutable field
# (created_at) to avoid pagination skips.
_STREAMS_REQUIRING_STABLE_SORT = [
    "addon",
    "customer",
    "differential_price",
    "hosted_page",
    "invoice",
    "item",
    "item_family",
    "item_price",
    "order",
    "payment_source",
    "plan",
    "subscription",
    "transaction",
    "virtual_bank_account",
]


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(_MANIFEST_PATH.read_text())


@pytest.mark.parametrize("stream_name", _STREAMS_REQUIRING_STABLE_SORT, ids=_STREAMS_REQUIRING_STABLE_SORT)
def test_sort_by_uses_immutable_created_at(manifest, stream_name):
    """sort_by must be created_at (immutable) — not updated_at — to avoid pagination skips."""
    stream_def = manifest["definitions"]["streams"][stream_name]
    sort_by = stream_def["retriever"]["requester"]["request_parameters"]["sort_by[asc]"]
    assert sort_by == "created_at", (
        f"Stream '{stream_name}' sorts by '{sort_by}' but must sort by 'created_at' "
        f"to prevent offset-based pagination from skipping records (see oncall/12026)."
    )
