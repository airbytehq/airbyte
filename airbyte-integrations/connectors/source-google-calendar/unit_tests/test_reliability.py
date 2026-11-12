#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pytest
from conftest import get_source
from jsonschema import Draft7Validator

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"credentials": {"auth_type": "manual", "client_id": "id", "client_secret": "secret", "refresh_token": "rt"}}
_BASE_URL = "https://www.googleapis.com/calendar/v3"


@pytest.mark.parametrize("overrides,expected", [({}, 3), ({"num_workers": None}, 3), ({"num_workers": 1}, 2), ({"num_workers": 5}, 5)])
def test_concurrency_preserves_saved_configs(overrides: dict, expected: int) -> None:
    config = {**_CONFIG, **overrides}
    source = get_source(config)
    definition = source._source_config["concurrency_level"]
    concurrency = ConcurrencyLevel(
        default_concurrency=definition["default_concurrency"], max_concurrency=definition["max_concurrency"], config=config, parameters={}
    )

    assert concurrency.get_concurrency_level() == expected
    spec = source.spec(logging.getLogger("test")).connectionSpecification
    assert spec["properties"]["num_workers"]["minimum"] == 1
    assert spec["properties"]["num_workers"]["maximum"] == 10


@pytest.mark.parametrize("stream,path", [("settings", "settings"), ("calendarlist", "calendarList")])
@pytest.mark.parametrize("empty", [False, True])
def test_list_page_sizes_and_tombstones(stream: str, path: str, empty: bool) -> None:
    params = {"maxResults": "250"}
    if stream == "calendarlist":
        params["showDeleted"] = "true"
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                "https://oauth2.googleapis.com/token", body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt"
            ),
            HttpResponse('{"access_token":"test-access-token","expires_in":3600}'),
        )
        first = HttpRequest(f"{_BASE_URL}/users/me/{path}", query_params=params)
        http_mocker.get(first, HttpResponse('{"items":[]}' if empty else '{"items":[{"id":"active"}],"nextPageToken":"p2"}'))
        if not empty:
            http_mocker.get(
                HttpRequest(f"{_BASE_URL}/users/me/{path}", query_params={**params, "pageToken": "p2"}),
                HttpResponse('{"items":[{"id":"removed","deleted":true}]}' if stream == "calendarlist" else '{"items":[{"id":"second"}]}'),
            )
        catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()

        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert output.errors == []
        assert [r.record.data["id"] for r in output.records] == (
            [] if empty else ["active", "removed" if stream == "calendarlist" else "second"]
        )
        if stream == "calendarlist" and not empty:
            assert output.records[-1].record.data["deleted"] is True


@pytest.mark.parametrize(
    "stream,properties",
    [
        (
            "calendarlist",
            {
                "dataOwner": "owner@example.com",
                "autoAcceptInvitations": True,
                "deleted": False,
                "summaryOverride": "Work",
                "location": "Office",
                "hidden": True,
            },
        ),
        (
            "calendars",
            {
                "workingHours": {
                    "workingHoursEnabled": True,
                    "availableTimes": [{"dayOfWeek": "monday", "periodStart": 540, "periodEnd": 1020}],
                }
            },
        ),
        (
            "events",
            {
                "focusTimeProperties": {
                    "chatStatus": "doNotDisturb",
                    "autoDeclineMode": "declineAllConflictingInvitations",
                    "declineMessage": "Busy",
                },
                "outOfOfficeProperties": {"autoDeclineMode": "declineNone", "declineMessage": "Away"},
                "workingLocationProperties": {
                    "type": "officeLocation",
                    "officeLocation": {"buildingId": "building", "floorId": "floor", "deskId": "desk"},
                },
                "eventLabelId": "label",
                "gadget": {"title": "Birthday", "height": 100},
                "locked": False,
                "attendeesOmitted": True,
                "birthdayProperties": {"type": "birthday", "contact": "people/person"},
                "colorId": "1",
            },
        ),
    ],
)
def test_additive_schema_fields_are_typed_and_nullable(stream: str, properties: dict) -> None:
    catalog = get_source(_CONFIG).discover(logging.getLogger("test"), _CONFIG)
    schema = next(s.json_schema for s in catalog.streams if s.name == stream)
    config = {**_CONFIG, "calendarid": "primary"}
    record = {"id": "primary", **properties}
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                "https://oauth2.googleapis.com/token", body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt"
            ),
            HttpResponse('{"access_token":"test-access-token","expires_in":3600}'),
        )
        if stream in ("calendarlist", "calendars"):
            params = {"maxResults": "250"}
            if stream == "calendarlist":
                params["showDeleted"] = "true"
            else:
                params.update({"showHidden": "true", "minAccessRole": "reader"})
            http_mocker.get(
                HttpRequest(f"{_BASE_URL}/users/me/calendarList", query_params=params),
                HttpResponse(json.dumps({"items": [record]})),
            )
        if stream in ("events", "calendars"):
            http_mocker.get(HttpRequest(f"{_BASE_URL}/calendars/primary"), HttpResponse(json.dumps(record)))
        if stream == "events":
            http_mocker.get(
                HttpRequest(
                    f"{_BASE_URL}/calendars/primary/events",
                    query_params={"showDeleted": "true", "maxResults": "2500", "singleEvents": "false"},
                ),
                HttpResponse(json.dumps({"items": [record]})),
            )
        output = read(get_source(config), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())
    assert output.errors == []
    assert len(output.records) == 1
    emitted = output.records[0].record.data
    Draft7Validator(schema).validate(emitted)
    for field, value in properties.items():
        assert emitted[field] == value
        declaration = schema["properties"][field]
        Draft7Validator.check_schema(declaration)
        validator = Draft7Validator(declaration)
        validator.validate(value)
        validator.validate(None)
        assert not validator.is_valid(42)


def test_credential_properties_have_unique_orders() -> None:
    spec = get_source(_CONFIG).spec(logging.getLogger("test")).connectionSpecification
    for option in spec["properties"]["credentials"]["oneOf"]:
        assert {name: prop["order"] for name, prop in option["properties"].items()} == {
            "auth_type": 0,
            "client_id": 1,
            "client_secret": 2,
            "refresh_token": 3,
        }
