# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_API = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_CATALOG = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()

_JANUARY = "2024-01-01T00:00:00.000Z"
_FEBRUARY = "2024-02-01T00:00:00.000Z"
_MARCH = "2024-03-01T00:00:00.000Z"
_APRIL = "2024-04-01T00:00:00.000Z"


def _page(page_id, last_edited_time):
    return {"object": "page", "id": page_id, "created_time": _JANUARY, "last_edited_time": last_edited_time, "properties": {}}


def _block(block_id, page_id, last_edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": page_id},
        "created_time": _JANUARY,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
    }


def _list(results):
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _read_blocks(requests_mock, state, nested_block_last_edited_time):
    """
    Two pages. page-1 holds block-1, which has one nested child; page-2 holds block-2 and block-3.
    Only the nested child's last_edited_time differs between the reads of a test.
    """
    requests_mock.post(f"{_API}/search", json=_list([_page("page-2", _MARCH), _page("page-1", _JANUARY)]))
    requests_mock.get(f"{_API}/blocks/page-1/children", json=_list([_block("block-1", "page-1", _JANUARY, has_children=True)]))
    requests_mock.get(f"{_API}/blocks/block-1/children", json=_list([_block("block-1-child", "page-1", nested_block_last_edited_time)]))
    requests_mock.get(
        f"{_API}/blocks/page-2/children",
        json=_list([_block("block-2", "page-2", _MARCH), _block("block-3", "page-2", _FEBRUARY)]),
    )
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=_CATALOG, state=state)


def _record_ids(output):
    # pages are read as concurrent partitions, so the order across pages is not deterministic
    return sorted(record.record.data["id"] for record in output.records)


def test_second_incremental_read_only_emits_blocks_edited_since_the_emitted_state(requests_mock):
    first_read = _read_blocks(requests_mock, StateBuilder().with_stream_state("blocks", {}).build(), _JANUARY)

    assert _record_ids(first_read) == ["block-1", "block-1-child", "block-2", "block-3"]
    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2024-03-01T00:00:00.000000Z"}

    requests_mock.reset_mock()
    second_read = _read_blocks(requests_mock, StateBuilder().with_stream_state("blocks", first_state).build(), _APRIL)

    # block-2 sits exactly on the state value and is repeated because the cursor boundary is inclusive.
    # block-1-child was edited after the state while its parent block-1 was not: it is still emitted.
    # block-1 and block-3 were not edited since the first read and are not emitted again.
    assert _record_ids(second_read) == ["block-1-child", "block-2"]
    assert second_read.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-04-01T00:00:00.000000Z"}
    # the filtering is client side: every page and nested block is still requested
    assert sorted(f"{request.method} {request.path}?{request.query}" for request in requests_mock.request_history) == [
        "GET /v1/blocks/block-1/children?page_size=100",
        "GET /v1/blocks/page-1/children?page_size=100",
        "GET /v1/blocks/page-2/children?page_size=100",
        "POST /v1/search?",
    ]
    assert second_read.errors == []
