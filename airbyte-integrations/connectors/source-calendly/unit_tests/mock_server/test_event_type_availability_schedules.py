# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from _helpers import CONFIG, ORGANIZATION_URI, collection, list_request, mock_user, read_stream, request
from conftest import _YAML_FILE_PATH, get_source
from freezegun import freeze_time
from jsonschema import Draft7Validator

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


STREAM = "event_type_availability_schedules"
EVENT_TYPES = [f"https://api.calendly.com/event_types/{name}" for name in ["a", "b"]]


def schedule(event_type: str, host: str) -> dict:
    return {
        "event_type": event_type,
        "availability_setting": "host",
        "availability_rule": {
            "uri": f"https://api.calendly.com/user_availability_schedules/{host}",
            "name": None,
            "user": f"https://api.calendly.com/users/{host}",
            "timezone": "America/New_York",
            "rules": [
                {"type": "wday", "wday": "monday", "intervals": [{"from": "09:00", "to": "17:00"}]},
                {"type": "date", "date": "2026-12-25", "intervals": []},
            ],
        },
    }


@pytest.mark.parametrize("deleted_parent", [False, True])
def test_availability_read_preserves_hosts_and_skips_deleted_event_types(deleted_parent: bool) -> None:
    parents = [{"uri": uri, "updated_at": "2024-01-01T00:00:00Z"} for uri in EVENT_TYPES]
    # Reusing a host schedule across event types and two hosts in one event type exercises both key columns.
    records = [schedule(EVENT_TYPES[0], "host-a"), schedule(EVENT_TYPES[0], "host-b"), schedule(EVENT_TYPES[1], "host-a")]
    targets = [request(STREAM, {"event_type": uri}) for uri in EVENT_TYPES]
    with HttpMocker() as http:
        user = mock_user(http)
        parent = list_request("event_types")
        http.get(parent, collection(parents))
        http.get(targets[0], collection(records[:2]))
        http.get(
            targets[1],
            (
                HttpResponse(body=json.dumps({"title": "Resource Not Found", "message": "Event type deleted"}), status_code=404)
                if deleted_parent
                else collection(records[2:])
            ),
        )

        output = read_stream(STREAM, sync_mode=SyncMode.full_refresh)

        assert not output.errors
        actual = [message.record.data for message in output.records]
        expected = records[:2] if deleted_parent else records
        assert sorted(actual, key=lambda r: (r["event_type"], r["availability_rule_uri"])) == [
            {**record, "availability_rule_uri": record["availability_rule"]["uri"]} for record in expected
        ]
        assert output.get_stream_statuses(STREAM)[-1].value == "COMPLETE"
        assert not any(message.log.level == Level.ERROR for message in output.logs)
        if deleted_parent:
            assert any(
                "/event_type_availability_schedules" in message.log.message and message.log.level == Level.INFO for message in output.logs
            )
        for target in [user, parent, *targets]:
            http.assert_number_of_calls(target, 1)

    discovered = discover(get_source(CONFIG), CONFIG).catalog.catalog
    stream = next(stream for stream in discovered.streams if stream.name == STREAM)
    assert stream.source_defined_primary_key == [["event_type"], ["availability_rule_uri"]]
    keys = [tuple(record[path[0]] for path in stream.source_defined_primary_key) for record in actual]
    assert len(set(keys)) == len(actual)
    for record in actual:
        Draft7Validator(stream.json_schema, format_checker=Draft7Validator.FORMAT_CHECKER).validate(record)
        assert set(record) <= stream.json_schema["properties"].keys()


@freeze_time("2024-02-01T00:00:00Z")
def test_full_refresh_availability_reads_unchanged_parents_with_incremental_event_types() -> None:
    saved = "2024-01-20T00:00:00.000000Z"
    parents = [
        {"uri": f"https://api.calendly.com/event_types/{name}", "updated_at": updated}
        for name, updated in [
            ("changed", "2024-01-25T00:00:00.000000Z"),
            ("unchanged-first-page", "2024-01-10T00:00:00.000000Z"),
            ("unchanged-second-page", "2024-01-05T00:00:00.000000Z"),
        ]
    ]
    state = (
        StateBuilder()
        .with_stream_state(
            "event_types",
            {
                "state": {"updated_at": saved},
                "states": [{"partition": {"organization_uri": ORGANIZATION_URI, "parent_slice": {}}, "cursor": {"updated_at": saved}}],
                "use_global_cursor": False,
                "lookback_window": 0,
                "parent_state": {},
            },
        )
        .build()
    )
    catalog = CatalogBuilder().with_stream("event_types", SyncMode.incremental).with_stream(STREAM, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=CONFIG, catalog=catalog, state=state)
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("event_types"), collection(parents[:2], "older-parents"))
        later_page = list_request("event_types", "older-parents")
        http.get(later_page, collection(parents[2:]))
        targets = [request(STREAM, {"event_type": parent["uri"]}) for parent in parents]
        for parent, target in zip(parents, targets):
            http.get(target, collection([schedule(parent["uri"], "host-a")]))

        output = read(source, CONFIG, catalog, state=state)

        assert not output.errors
        assert [message.record.data for message in output.records if message.record.stream == "event_types"] == parents[:1]
        availability = [message.record.data for message in output.records if message.record.stream == STREAM]
        assert {record["event_type"] for record in availability} == {parent["uri"] for parent in parents}
        assert len(availability) == len(parents)
        for name in ["event_types", STREAM]:
            assert output.get_stream_statuses(name)[-1].value == "COMPLETE"
        for target in [later_page, *targets]:
            http.assert_number_of_calls(target, 1)
