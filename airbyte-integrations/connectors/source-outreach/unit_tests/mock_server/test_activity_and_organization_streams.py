# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
from jsonschema import validate

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source

from .config import ConfigBuilder
from .request_builder import OutreachRequestBuilder
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids, stream_state


CASES = [
    (
        "events",
        "/events",
        "event",
        "createdAt",
        {"name": "note_created", "payload": {"text": "note"}, "body": "Note", "eventAt": "2020-01-01T00:00:00.000Z"},
        {"user": [7], "plugin": [9]},
    ),
    ("teams", "/teams", "team", "updatedAt", {"name": "Sales", "color": "#5951ff"}, {"users": [7, 8], "creator": [9]}),
    ("roles", "/roles", "role", "updatedAt", {"name": "Manager", "externalId": "role-1"}, {"parentRole": [7]}),
    (
        "profiles",
        "/profiles",
        "profile",
        "updatedAt",
        {"name": "Standard", "isAdmin": False, "systemInternal": True, "globalId": "profile-1"},
        {},
    ),
    ("duties", "/duties", "duty", None, {"dutyType": "admin", "symbolicName": "manage"}, {}),
    (
        "rulesets",
        "/rulesets",
        "ruleset",
        "updatedAt",
        {
            "name": "Default",
            "includeUnsubscribeLinks": True,
            "dependentFields": [],
            "duplicateType": "email",
            "skipCallTasksWithInvalidPhone": True,
        },
        {"owner": [7], "sequences": [8, 9]},
    ),
    (
        "favorites",
        "/favorites",
        "favorite",
        "updatedAt",
        {"targetId": 8, "targetType": "sequence"},
        {"creator": [7], "target": [8], "user": [7]},
    ),
    (
        "mail_aliases",
        "/mailAliases",
        "mailAlias",
        "updatedAt",
        {"canSend": True, "email": "alias@example.com", "emailHash": "hash"},
        {"mailbox": [7]},
    ),
]
PARAMS = "name,path,resource_type,cursor,attributes,relationships"
FIRST = "2024-01-02T03:04:05.000Z"
NEWEST = "2024-01-03T03:04:05.123Z"
ADVANCED = "2024-02-01T00:00:00.000Z"


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def _request(path: str, cursor: str | None) -> OutreachRequestBuilder:
    return OutreachRequestBuilder.endpoint(path).with_cursor_field(cursor)


def _resource(resource_type: str, cursor: str | None, attributes: dict, relationships: dict, record_id: int, timestamp: str) -> dict:
    attrs = {**attributes, **({cursor: timestamp} if cursor else {})}
    rels = {key: {"data": [{"type": key, "id": value} for value in values]} for key, values in relationships.items()}
    if rels:
        key = next(iter(rels))
        if len(rels[key]["data"]) == 1:
            rels[key]["data"] = rels[key]["data"][0]
    return resource(record_id, resource_type, attrs, rels)


@pytest.mark.parametrize(PARAMS, CASES)
def test_full_refresh_flattens_attributes_and_relationships(http_mocker, name, path, resource_type, cursor, attributes, relationships):
    given_token(http_mocker)
    http_mocker.get(_request(path, cursor).build(), page_response([_resource(resource_type, cursor, attributes, relationships, 1, FIRST)]))

    output = read_stream(name, SyncMode.full_refresh)

    assert not output.errors
    expected = {"id": 1, **attributes, **relationships, **({cursor: FIRST} if cursor else {})}
    assert [record.record.data for record in output.records] == [expected]
    config = ConfigBuilder().build()
    schema = next(
        stream.json_schema for stream in build_source(config).discover(logging.getLogger(), config).streams if stream.name == name
    )
    assert set(expected) <= set(schema["properties"])
    validate(expected, schema)


@pytest.mark.parametrize(PARAMS, CASES)
def test_pagination_follows_links_next_until_absent(http_mocker, name, path, resource_type, cursor, attributes, relationships):
    given_token(http_mocker)
    request = _request(path, cursor)
    next_url = request.next_page_url("opaque-next-cursor")
    http_mocker.get(
        request.build(), page_response([_resource(resource_type, cursor, attributes, relationships, 1, FIRST)], next_url=next_url)
    )
    http_mocker.get(HttpRequest(next_url), page_response([_resource(resource_type, cursor, attributes, relationships, 2, NEWEST)]))

    output = read_stream(name, SyncMode.full_refresh)

    assert not output.errors
    assert record_ids(output) == [1, 2]


@pytest.mark.parametrize(PARAMS, [case for case in CASES if case[3]])
def test_incremental_round_trip_uses_emitted_cursor(http_mocker, name, path, resource_type, cursor, attributes, relationships):
    given_token(http_mocker)
    http_mocker.get(
        _request(path, cursor).build(),
        page_response(
            [
                _resource(resource_type, cursor, attributes, relationships, 1, FIRST),
                _resource(resource_type, cursor, attributes, relationships, 2, NEWEST),
            ]
        ),
    )

    first = read_stream(name, SyncMode.incremental)

    assert not first.errors
    assert record_ids(first) == [1, 2]
    saved = stream_state(first)
    assert saved == {cursor: NEWEST}
    state = StateBuilder().with_stream_state(name, saved).build()
    http_mocker.get(
        _request(path, cursor).with_updated_since(saved[cursor]).build(),
        page_response(
            [
                _resource(resource_type, cursor, attributes, relationships, 2, NEWEST),
                _resource(resource_type, cursor, attributes, relationships, 3, ADVANCED),
            ]
        ),
    )

    second = read_stream(name, SyncMode.incremental, state=state)

    assert not second.errors
    assert record_ids(second) == [2, 3]
    assert stream_state(second) == {cursor: ADVANCED}


@pytest.mark.parametrize(PARAMS, CASES)
def test_empty_response_completes_without_records(http_mocker, name, path, resource_type, cursor, attributes, relationships):
    given_token(http_mocker)
    http_mocker.get(_request(path, cursor).build(), page_response([]))

    output = read_stream(name, SyncMode.incremental if cursor else SyncMode.full_refresh)

    assert not output.errors
    assert output.records == []
    assert output.get_stream_statuses(name) == [AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE]
