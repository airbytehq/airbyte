# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "API Key",
        "api_key": "test_api_key",
    },
    "is_sandbox": False,
    "start_date": "2021-01-01",
    "include_deleted_objects": False,
}

_TIMECARDS_SEARCH_URL = "https://connect.squareup.com/v2/labor/timecards/search"
_SHIFTS_SEARCH_URL = "https://connect.squareup.com/v2/labor/shifts/search"


def _timecard(timecard_id: str) -> dict:
    return {
        "id": timecard_id,
        "team_member_id": "TEAM_MEMBER_1",
        "location_id": "LOCATION_1",
        "start_at": "2024-01-02T10:00:00.000000Z",
        "end_at": "2024-01-02T18:00:00.000000Z",
        "wage": {
            "title": "Team Member",
            "hourly_rate": {"amount": 2500, "currency": "USD"},
            "job_id": "JOB_1",
            "tip_eligible": True,
        },
        "status": "CLOSED",
        "version": 1,
        "created_at": "2024-01-02T10:00:00.000000Z",
        "updated_at": "2024-01-02T18:00:00.000000Z",
    }


def _sync():
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("shifts", SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog)


def test_shifts_stream_reads_from_timecards_endpoint():
    timecards = {"timecards": [_timecard("timecard-1"), _timecard("timecard-2")]}

    with requests_mock.Mocker() as mocker:
        timecards_matcher = mocker.post(_TIMECARDS_SEARCH_URL, json=timecards)
        output = _sync()

    records = [record.record.data for record in output.records]
    assert [record["id"] for record in records] == ["timecard-1", "timecard-2"]
    assert timecards_matcher.call_count == 1
    assert mocker.request_history[-1].headers["Square-Version"] == "2025-05-21"
    assert all(record["employee_id"] == record["team_member_id"] for record in records)


def test_shifts_stream_does_not_call_retired_shifts_endpoint():
    timecards = {"timecards": [_timecard("timecard-1"), _timecard("timecard-2")]}

    with requests_mock.Mocker() as mocker:
        shifts_matcher = mocker.post(
            _SHIFTS_SEARCH_URL,
            status_code=410,
            json={"errors": [{"category": "API_ERROR", "code": "GONE"}]},
        )
        mocker.post(_TIMECARDS_SEARCH_URL, json=timecards)
        output = _sync()

    records = [record.record.data for record in output.records]
    assert shifts_matcher.call_count == 0
    assert [record["id"] for record in records] == ["timecard-1", "timecard-2"]


def test_shifts_stream_follows_cursor_across_pages():
    pages = {
        None: {"timecards": [_timecard(f"timecard-{i}") for i in range(3)], "cursor": "cursor-page-2"},
        "cursor-page-2": {"timecards": [_timecard(f"timecard-{i}") for i in range(3, 6)], "cursor": "cursor-page-3"},
        "cursor-page-3": {"timecards": [_timecard(f"timecard-{i}") for i in range(6, 8)]},
    }
    request_bodies = []

    def _timecards_response(request, context):
        body = json.loads(request.text) if request.text else {}
        request_bodies.append(body)
        return pages[body.get("cursor")]

    with requests_mock.Mocker() as mocker:
        timecards_matcher = mocker.post(_TIMECARDS_SEARCH_URL, json=_timecards_response)
        output = _sync()

    assert [record.record.data["id"] for record in output.records] == [f"timecard-{i}" for i in range(8)]
    assert timecards_matcher.call_count == 3
    assert [body.get("cursor") for body in request_bodies] == [None, "cursor-page-2", "cursor-page-3"]
    assert all(body["limit"] == 200 for body in request_bodies)


def test_shifts_stream_copies_team_member_id_into_employee_id_as_string():
    timecard_without_team_member = _timecard("timecard-2")
    timecard_without_team_member["team_member_id"] = None
    numeric_looking = _timecard("timecard-3")
    numeric_looking["team_member_id"] = "12345"
    timecards = {"timecards": [_timecard("timecard-1"), timecard_without_team_member, numeric_looking]}

    with requests_mock.Mocker() as mocker:
        mocker.post(_TIMECARDS_SEARCH_URL, json=timecards)
        output = _sync()

    records = {record.record.data["id"]: record.record.data for record in output.records}
    assert records["timecard-1"]["employee_id"] == "TEAM_MEMBER_1"
    assert "employee_id" not in records["timecard-2"]
    assert records["timecard-3"]["employee_id"] == "12345"
