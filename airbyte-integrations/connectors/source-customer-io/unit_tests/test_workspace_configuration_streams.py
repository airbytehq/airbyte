# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `subscription_topics`, `object_types`, `workspaces`, `reporting_webhooks`, `snippets` and `collections`."""

import logging

import pytest
import requests_mock
from _helpers import get_source
from test_error_handling_and_lookback import _API, _PRIOR_CURSOR, _START_DATE, _START_EPOCH
from test_pagination_region_incremental import _BASE_CONFIG, _read

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


def _topic(topic_id: int) -> dict:
    return {
        "id": topic_id,
        "identifier": f"topic_{topic_id}",
        "name": f"topic-{topic_id}",
        "description": "Product news",
        "subscribed_by_default": True,
    }


def _object_type(type_id: int) -> dict:
    """The spec types `id` as a string: object type ids are integers passed as strings."""
    return {
        "id": str(type_id),
        "name": "Companies",
        "singular_name": "Company",
        "slug": "companies",
        "singular_slug": "company",
        "icon": "building",
        "enabled": True,
    }


def _workspace(workspace_id: int) -> dict:
    """Counts for the current billing period, with no update time."""
    return {
        "id": workspace_id,
        "name": f"workspace-{workspace_id}",
        "messages_sent": 3,
        "billable_messages_sent": 3,
        "people": 121,
        "object_types": 0,
        "objects": 0,
    }


def _webhook(webhook_id: int) -> dict:
    return {
        "id": webhook_id,
        "name": f"webhook-{webhook_id}",
        "type": "webhook",
        "endpoint": f"https://example.com/hooks/{webhook_id}",
        "events": ["email_clicked", "email_opened", "email_sent"],
        "disabled": False,
        "full_resolution": False,
        "with_content": False,
    }


def _snippet(number: int, updated_at: int = _PRIOR_CURSOR) -> dict:
    """No `id`: the spec documents `name` as unique, so it is the primary key."""
    return {"name": f"snippet-{number}", "value": "<p>Thanks!</p>", "updated_at": updated_at}


def _collection(collection_id: int, updated_at: int = _PRIOR_CURSOR) -> dict:
    """Metadata only: the list returns each collection's keys and size, not its contents."""
    return {
        "id": collection_id,
        "name": f"products-{collection_id}",
        "schema": ["id", "name"],
        "rows": 1,
        "bytes": 25,
        "created_at": updated_at,
        "updated_at": updated_at,
    }


# Stream >> (request path, records key, record builder)
_LISTS = {
    "subscription_topics": ("subscription_topics", "topics", _topic),
    "object_types": ("object_types", "types", _object_type),
    "workspaces": ("workspaces", "workspaces", _workspace),
    "reporting_webhooks": ("reporting_webhooks", "reporting_webhooks", _webhook),
    "snippets": ("snippets", "snippets", _snippet),
    "collections": ("collections", "collections", _collection),
}
_INCREMENTAL = ["snippets"]


def test_discover_declares_primary_keys_cursors_and_sync_modes():
    """Keys follow the vendor spec; only `snippets` syncs incrementally. `collections` returns `updated_at`, but replacing its
    contents may not move it, so it is full refresh like the streams without an update time."""
    full_refresh, incremental = [SyncMode.full_refresh], [SyncMode.full_refresh, SyncMode.incremental]
    expected = {
        "subscription_topics": ([["id"]], None, full_refresh),
        "object_types": ([["id"]], None, full_refresh),
        "workspaces": ([["id"]], None, full_refresh),
        "reporting_webhooks": ([["id"]], None, full_refresh),
        "snippets": ([["name"]], ["updated_at"], incremental),
        "collections": ([["id"]], None, full_refresh),
    }
    catalog = get_source(_BASE_CONFIG).discover(logging.getLogger("airbyte"), _BASE_CONFIG)
    declared = {
        stream.name: (stream.source_defined_primary_key, stream.default_cursor_field, stream.supported_sync_modes)
        for stream in catalog.streams
    }
    assert {name: declared.get(name) for name in expected} == expected
    object_types = next(stream for stream in catalog.streams if stream.name == "object_types")
    assert object_types.json_schema["properties"]["id"]["type"] == ["null", "string"]


@pytest.mark.parametrize("stream_name", list(_LISTS))
def test_list_stream_reads_the_whole_list_in_one_request_without_query_parameters(stream_name):
    """No paginator is documented, so one request returns the list unchanged; `collections` never requests a collection's contents."""
    path, records_key, build = _LISTS[stream_name]
    records = [build(1), build(2)]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: records})
        output = _read(stream_name, _BASE_CONFIG)

    assert [record.record.data for record in output.records] == records
    assert not output.errors
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE
    assert [(request.path, request.qs) for request in mocker.request_history] == [(f"/v1/{path}", {})]


@pytest.mark.parametrize("stream_name", list(_LISTS))
def test_empty_list_ends_complete_without_records(stream_name):
    """`getTopics` returns an empty `topics` array when the workspace has no topics, as in the test workspace."""
    path, records_key, _ = _LISTS[stream_name]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: []})
        output = _read(stream_name, _BASE_CONFIG)

    assert not output.records
    assert not output.errors
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE
    assert mocker.call_count == 1


@pytest.mark.parametrize(
    "endpoint, synced",
    [
        ("https://user:p%40ss@hooks.example.com/in?x=1", "https://hooks.example.com/in?x=1"),
        ("https://u:raw@pw@host.example/p", "https://host.example/p"),
        ("http://username:password@example.com", "http://example.com"),
        ("HTTPS://user:pw@example.com/x", "HTTPS://example.com/x"),
        ("https://hooks.example.com/in?token=abc", "https://hooks.example.com/in?token=abc"),
        ("https://hooks.example.com/r?next=http://a@b", "https://hooks.example.com/r?next=http://a@b"),
        ("https://example.com/a@b/c", "https://example.com/a@b/c"),
        ("", ""),
        (None, None),
    ],
)
def test_reporting_webhooks_strip_basic_auth_userinfo_from_the_endpoint(endpoint, synced):
    """Customer.io documents `username:password@` in the URL as the way to secure a webhook, so it is removed; anything after
    the host, such as a token in the path or query, is kept, and an empty or missing endpoint is left as is."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/reporting_webhooks", json={"reporting_webhooks": [{**_webhook(1), "endpoint": endpoint}]})
        output = _read("reporting_webhooks", _BASE_CONFIG)

    assert [record.record.data.get("endpoint") for record in output.records] == [synced]


def test_collections_ignore_start_date_and_return_every_collection():
    """Full refresh only: a collection last updated before the Start Date is still read, with its current counts."""
    records = [_collection(1, _START_EPOCH - 1), _collection(2, _PRIOR_CURSOR)]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/collections", json={"collections": records})
        output = _read("collections", {**_BASE_CONFIG, "start_date": _START_DATE})

    assert [record.record.data for record in output.records] == records


@pytest.mark.parametrize("stream_name", _INCREMENTAL)
def test_incremental_stream_resumes_from_state_with_one_hour_lookback(stream_name):
    """A resumed read re-emits records down to one hour below the saved cursor and advances the state to the newest record."""
    path, records_key, build = _LISTS[stream_name]
    records = [build(1, _PRIOR_CURSOR - 3601), build(2, _PRIOR_CURSOR - 3600), build(3, _PRIOR_CURSOR), build(4, _PRIOR_CURSOR + 10)]
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": str(_PRIOR_CURSOR)}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: records})
        output = _read(stream_name, _BASE_CONFIG, SyncMode.incremental, state)

    assert [record.record.data for record in output.records] == records[1:]
    assert int(output.most_recent_state.stream_state.updated_at) == _PRIOR_CURSOR + 10
    assert [(request.path, request.qs) for request in mocker.request_history] == [(f"/v1/{path}", {})]


@pytest.mark.parametrize(
    "saved_cursor, final_cursor",
    [(None, _PRIOR_CURSOR - 1800), (_PRIOR_CURSOR, _PRIOR_CURSOR)],
    ids=["first_sync", "inside_lookback"],
)
@pytest.mark.parametrize("stream_name", _INCREMENTAL)
def test_start_date_floors_the_first_sync_and_the_lookback(stream_name, saved_cursor, final_cursor):
    """Records below the Start Date are dropped on a first sync and inside the lookback of a resumed one; the state never moves back."""
    path, records_key, build = _LISTS[stream_name]
    records = [build(1, _START_EPOCH - 1), build(2, _START_EPOCH), build(3, _PRIOR_CURSOR - 1800)]
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": str(saved_cursor)}).build() if saved_cursor else None
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: records})
        output = _read(stream_name, {**_BASE_CONFIG, "start_date": _START_DATE}, SyncMode.incremental, state)

    assert [record.record.data for record in output.records] == records[1:]
    assert int(output.most_recent_state.stream_state.updated_at) == final_cursor
