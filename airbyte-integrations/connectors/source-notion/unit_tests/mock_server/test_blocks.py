# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CONFIG = {
    "start_date": "2026-01-01T00:00:00.000Z",
    "credentials": {"auth_type": "token", "token": "test-token"},
    "num_workers": 1,
}
BASE_URL = "https://api.notion.com/v1/"


def block(block_id: str, edited: str, has_children: bool = False) -> dict:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "parent": {"type": "page_id", "page_id": "page-1"},
        "last_edited_time": edited,
        "has_children": has_children,
        "paragraph": {"rich_text": []},
    }


def response(records: list[dict], next_cursor: str | None = None) -> dict:
    return {"object": "list", "results": records, "has_more": next_cursor is not None, "next_cursor": next_cursor}


def read_blocks(state: list | None = None):
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    return read(get_source(CONFIG, state), CONFIG, catalog, state=state)


@freeze_time("2026-01-06T00:00:00Z")
def test_incremental_read_resumes_state_and_traverses_unchanged_ancestors(requests_mock):
    requests_mock.post(
        BASE_URL + "search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": "2026-01-05T00:00:00.000Z", "properties": {}}]),
    )
    ancestor = block("ancestor", "2026-01-01T00:00:00.000Z", has_children=True)
    boundary = block("boundary", "2026-01-03T00:00:00.000Z")
    requests_mock.get(BASE_URL + "blocks/page-1/children?page_size=100", json=response([ancestor, boundary]), complete_qs=True)
    requests_mock.get(
        BASE_URL + "blocks/ancestor/children?page_size=100",
        json=response([block("nested", "2026-01-02T00:00:00.000Z")]),
        complete_qs=True,
    )
    initial = read_blocks()
    assert not initial.errors
    assert [record.record.data["id"] for record in initial.records] == ["nested", "ancestor", "boundary"]
    assert initial.most_recent_state.stream_state.__dict__ == {
        "state": {"last_edited_time": "2026-01-03T00:00:00.000000Z"},
        "lookback_window": 0,
        "parent_state": {},
        "use_global_cursor": True,
    }
    state = StateBuilder().with_stream_state("blocks", initial.most_recent_state.stream_state.__dict__).build()

    requests_mock.get(
        BASE_URL + "blocks/page-1/children?page_size=100",
        json=response([ancestor, boundary], next_cursor="second-page"),
        complete_qs=True,
    )
    requests_mock.get(
        BASE_URL + "blocks/page-1/children?page_size=100&start_cursor=second-page",
        json=response([block("old-sibling", "2026-01-02T00:00:00.000Z"), block("new", "2026-01-05T00:00:00.000Z")]),
        complete_qs=True,
    )
    requests_mock.get(
        BASE_URL + "blocks/ancestor/children?page_size=100",
        json=response([block("nested", "2026-01-04T00:00:00.000Z")]),
        complete_qs=True,
    )
    requests_mock.reset_mock()
    resumed = read_blocks(state)
    assert not resumed.errors
    assert [record.record.data["id"] for record in resumed.records] == ["nested", "boundary", "new"]
    assert resumed.most_recent_state.stream_state.__dict__ == {
        "state": {"last_edited_time": "2026-01-05T00:00:00.000000Z"},
        "lookback_window": 0,
        "parent_state": {},
        "use_global_cursor": True,
    }
    search_requests = [request for request in requests_mock.request_history if request.method == "POST"]
    assert [request.json() for request in search_requests] == [
        {
            "page_size": 100,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": "page"},
        }
    ]
    assert sorted(request.path_url for request in requests_mock.request_history if request.method == "GET") == sorted(
        [
            "/v1/blocks/page-1/children?page_size=100",
            "/v1/blocks/page-1/children?start_cursor=second-page&page_size=100",
            "/v1/blocks/ancestor/children?page_size=100",
        ]
    )


@freeze_time("2026-01-06T00:00:00Z")
def test_initial_incremental_read_filters_before_start_date_without_pruning_children(requests_mock):
    requests_mock.post(
        BASE_URL + "search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": "2026-01-05T00:00:00.000Z", "properties": {}}]),
    )
    requests_mock.get(
        BASE_URL + "blocks/page-1/children?page_size=100",
        json=response([block("old-parent", "2025-12-31T00:00:00.000Z", has_children=True)]),
        complete_qs=True,
    )
    requests_mock.get(
        BASE_URL + "blocks/old-parent/children?page_size=100",
        json=response([block("boundary", CONFIG["start_date"]), block("new-child", "2026-01-02T00:00:00.000Z")]),
        complete_qs=True,
    )
    output = read_blocks()
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["boundary", "new-child"]
    assert output.most_recent_state.stream_state.__dict__ == {
        "state": {"last_edited_time": "2026-01-02T00:00:00.000000Z"},
        "lookback_window": 0,
        "parent_state": {},
        "use_global_cursor": True,
    }
