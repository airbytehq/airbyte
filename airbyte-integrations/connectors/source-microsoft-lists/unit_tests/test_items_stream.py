#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any

from conftest import get_source

from airbyte_cdk.models import AirbyteStateType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "site_id": "site-id",
    "client_id": "test-client",
    "client_secret": "test-secret",
    "application_id_uri": "https://graph.microsoft.com/.default",
    "tenant_id": "test-tenant",
    "domain": "example.com",
}
_TOKEN_URL = "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token"
_TOKEN_REQUEST = HttpRequest(
    _TOKEN_URL,
    body="grant_type=client_credentials&client_id=test-client&client_secret=test-secret&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "access-token", "expires_in": 3600}))
_GRAPH_ROOT = "https://graph.microsoft.com/v1.0/sites/site-id"
_LISTS_URL = f"{_GRAPH_ROOT}/lists"
_NEXT_LINK_A = f"{_GRAPH_ROOT}/lists/A/items/delta?$skiptoken=page-a"
_DELTA_LINK_A = f"{_GRAPH_ROOT}/lists/A/items/delta?$deltatoken=delta-a"
_DELTA_LINK_B = f"{_GRAPH_ROOT}/lists/B/items/delta?$deltatoken=delta-b"
_DELTA_LINK_A_NEW = f"{_GRAPH_ROOT}/lists/A/items/delta?$deltatoken=delta-a-new"
_DELTA_LINK_B_NEW = f"{_GRAPH_ROOT}/lists/B/items/delta?$deltatoken=delta-b-new"


def _items_delta_url(list_id: str) -> str:
    return f"{_GRAPH_ROOT}/lists/{list_id}/items/delta"


def _items_url(list_id: str) -> str:
    return f"{_GRAPH_ROOT}/lists/{list_id}/items"


def _catalog(stream_name: str, sync_mode: SyncMode):
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _read(http_mocker: HttpMocker, stream_name: str, sync_mode: SyncMode, state=None):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    source = get_source(_CONFIG, state=state)
    return read(source, _CONFIG, _catalog(stream_name, sync_mode), state=state)


def _mock_lists(http_mocker: HttpMocker, *list_ids: str) -> None:
    http_mocker.get(
        HttpRequest(_LISTS_URL),
        HttpResponse(json.dumps({"value": [{"id": list_id} for list_id in list_ids]})),
    )


def _state_for_tokens(tokens: dict[str, str]):
    return (
        StateBuilder()
        .with_stream_state(
            "items",
            {
                "state_type": "sync_token",
                "states": [
                    {
                        "partition": {"list": list_id, "parent_slice": {}},
                        "cursor": {"token": token, "committed_at": "2026-01-01T00:00:00Z"},
                    }
                    for list_id, token in tokens.items()
                ],
            },
        )
        .build()
    )


def _state_payload(message) -> dict[str, Any]:
    return json.loads(json.dumps(message.state.stream.stream_state, default=lambda value: value.__dict__))


def _stream_states(output) -> list[dict[str, Any]]:
    return [
        _state_payload(message)
        for message in output.state_messages
        if message.state.type == AirbyteStateType.STREAM and message.state.stream.stream_descriptor.name == "items"
    ]


def _latest_tokens(output) -> dict[str, str]:
    states = _stream_states(output)
    assert states, "expected items stream state"
    return {item["partition"]["list"]: item["cursor"]["token"] for item in states[-1]["states"]}


def _assert_no_next_link_is_committed(output, next_links: set[str]) -> None:
    for state in _stream_states(output):
        for partition_state in state.get("states", []):
            token = partition_state.get("cursor", {}).get("token")
            assert token not in next_links


def _record_data(output) -> list[dict[str, Any]]:
    return [message.record.data for message in output.records]


def _run_cold_sync():
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A", "B")
        http_mocker.get(
            HttpRequest(_items_delta_url("A")),
            HttpResponse(
                json.dumps(
                    {
                        "value": [{"id": "a1", "fields": {"Title": "first"}}],
                        "@odata.nextLink": _NEXT_LINK_A,
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(_NEXT_LINK_A),
            HttpResponse(
                json.dumps(
                    {
                        "value": [{"id": "a2", "fields": {"Title": "second"}}],
                        "@odata.deltaLink": _DELTA_LINK_A,
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(_items_delta_url("B")),
            HttpResponse(json.dumps({"value": [], "@odata.deltaLink": _DELTA_LINK_B})),
        )
        return _read(http_mocker, "items", SyncMode.incremental)


def test_discover_items_supports_full_refresh_and_incremental_without_cursor_field():
    discovered = get_source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG)
    streams = {stream.name: stream for stream in discovered.streams}

    assert streams["items"].supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
    assert streams["items"].source_defined_cursor is True
    assert streams["items"].default_cursor_field == []
    for stream_name in ("lists", "listcontenttypes", "listitems", "columnvalues"):
        assert streams[stream_name].supported_sync_modes == [SyncMode.full_refresh]


def test_cold_incremental_sync_paginates_each_list_and_commits_delta_links():
    output = _run_cold_sync()

    assert output.errors == []
    assert _record_data(output) == [
        {"id": "a1", "fields": {"Title": "first"}, "item_info": {"list_id": "A", "item_id": "a1"}},
        {"id": "a2", "fields": {"Title": "second"}, "item_info": {"list_id": "A", "item_id": "a2"}},
    ]
    assert _latest_tokens(output) == {"A": _DELTA_LINK_A, "B": _DELTA_LINK_B}
    _assert_no_next_link_is_committed(output, {_NEXT_LINK_A})


def test_warm_incremental_sync_replays_emitted_partition_tokens_and_emits_tombstones():
    cold_output = _run_cold_sync()
    state = [message.state for message in cold_output.state_messages]
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A", "B")
        http_mocker.get(
            HttpRequest(_DELTA_LINK_A),
            HttpResponse(
                json.dumps(
                    {
                        "value": [
                            {"id": "a1", "fields": {"Title": "updated"}},
                            {"id": "a2", "deleted": {"state": "deleted"}},
                        ],
                        "@odata.deltaLink": _DELTA_LINK_A_NEW,
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(_DELTA_LINK_B),
            HttpResponse(json.dumps({"value": [], "@odata.deltaLink": _DELTA_LINK_B_NEW})),
        )
        output = _read(http_mocker, "items", SyncMode.incremental, state=state)

    records = _record_data(output)
    assert output.errors == []
    assert [record["id"] for record in records] == ["a1", "a2"]
    assert records[0]["fields"] == {"Title": "updated"}
    assert records[1]["deleted"]["state"] == "deleted"
    assert records[0]["item_info"] == {"list_id": "A", "item_id": "a1"}
    assert records[1]["item_info"] == {"list_id": "A", "item_id": "a2"}
    assert _latest_tokens(output) == {"A": _DELTA_LINK_A_NEW, "B": _DELTA_LINK_B_NEW}


def test_expired_delta_link_resets_only_its_partition_and_restarts_from_delta_endpoint():
    token_a = f"{_items_delta_url('A')}?$deltatoken=expired"
    token_b = f"{_items_delta_url('B')}?$deltatoken=stored-b"
    state = _state_for_tokens({"A": token_a, "B": token_b})
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A", "B")
        http_mocker.get(
            HttpRequest(token_a),
            HttpResponse(
                json.dumps(
                    {
                        "error": {
                            "code": "resyncChangesApplyDifferences",
                            "message": "The delta token has expired.",
                        }
                    }
                ),
                status_code=410,
            ),
        )
        http_mocker.get(
            HttpRequest(_items_delta_url("A")),
            HttpResponse(
                json.dumps(
                    {
                        "value": [{"id": "a-new", "fields": {"Title": "resynced"}}],
                        "@odata.deltaLink": _DELTA_LINK_A_NEW,
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(token_b),
            HttpResponse(json.dumps({"value": [], "@odata.deltaLink": _DELTA_LINK_B_NEW})),
        )
        output = _read(http_mocker, "items", SyncMode.incremental, state=state)

    assert output.errors == []
    assert [record["id"] for record in _record_data(output)] == ["a-new"]
    assert _latest_tokens(output) == {"A": _DELTA_LINK_A_NEW, "B": _DELTA_LINK_B_NEW}


def test_missing_partition_state_bootstraps_only_new_list():
    stored_link_a = f"{_items_delta_url('A')}?$deltatoken=stored-a"
    state = _state_for_tokens({"A": stored_link_a})
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A", "C")
        http_mocker.get(
            HttpRequest(stored_link_a),
            HttpResponse(json.dumps({"value": [], "@odata.deltaLink": _DELTA_LINK_A_NEW})),
        )
        http_mocker.get(
            HttpRequest(_items_delta_url("C")),
            HttpResponse(json.dumps({"value": [], "@odata.deltaLink": "new-list-c-token"})),
        )
        output = _read(http_mocker, "items", SyncMode.incremental, state=state)

    assert output.errors == []
    assert _latest_tokens(output) == {"A": _DELTA_LINK_A_NEW, "C": "new-list-c-token"}


def test_full_refresh_without_state_starts_at_delta_endpoint():
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A", "B")
        http_mocker.get(
            HttpRequest(_items_delta_url("A")),
            HttpResponse(
                json.dumps(
                    {
                        "value": [{"id": "a1", "fields": {"Title": "full refresh A"}}],
                        "@odata.deltaLink": _DELTA_LINK_A_NEW,
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(_items_delta_url("B")),
            HttpResponse(
                json.dumps(
                    {
                        "value": [{"id": "b1", "fields": {"Title": "full refresh B"}}],
                        "@odata.deltaLink": _DELTA_LINK_B_NEW,
                    }
                )
            ),
        )
        output = _read(http_mocker, "items", SyncMode.full_refresh)

    assert output.errors == []
    assert _record_data(output) == [
        {
            "id": "a1",
            "fields": {"Title": "full refresh A"},
            "item_info": {"list_id": "A", "item_id": "a1"},
        },
        {
            "id": "b1",
            "fields": {"Title": "full refresh B"},
            "item_info": {"list_id": "B", "item_id": "b1"},
        },
    ]


def test_listitems_child_reads_parent_items_endpoint_not_delta_endpoint():
    with HttpMocker() as http_mocker:
        _mock_lists(http_mocker, "A")
        http_mocker.get(
            HttpRequest(_items_url("A")),
            HttpResponse(json.dumps({"value": [{"id": "item-1"}]})),
        )
        http_mocker.get(
            HttpRequest(f"{_items_url('A')}/item-1"),
            HttpResponse(json.dumps({"id": "item-1", "fields": {"Title": "child"}})),
        )
        output = _read(http_mocker, "listitems", SyncMode.full_refresh)

    assert output.errors == []
    assert _record_data(output) == [{"id": "item-1", "fields": {"Title": "child"}}]
