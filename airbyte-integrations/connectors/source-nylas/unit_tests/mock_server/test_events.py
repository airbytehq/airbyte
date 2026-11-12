# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_API_KEY = "test_api_key"
_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant_1"
_START_DATE = "2026-09-01T00:00:00Z"
_END_DATE = "2026-09-03T00:00:00Z"
_CONFIG = {"api_key": _API_KEY, "api_server": "us", "start_date": _START_DATE, "end_date": _END_DATE}


def _epoch(value: str) -> str:
    return str(int(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()))


def _request(path: str, query_params: dict) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params=query_params, headers={"Authorization": f"Bearer {_API_KEY}"})


def _response(data: list, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": data}), status_code=status_code)


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        f"/grants/{_GRANT_ID}/events",
        {"limit": "50", "calendar_id": calendar_id, "start": _epoch(_START_DATE), "end": _epoch(_END_DATE)},
    )


def _given_grant_with_calendars(http_mocker: HttpMocker, calendar_ids: list) -> None:
    http_mocker.get(_request("/grants", {"limit": "50"}), _response([{"id": _GRANT_ID}]))
    http_mocker.get(
        _request(f"/grants/{_GRANT_ID}/calendars", {"limit": "50"}),
        _response([{"id": calendar_id, "grant_id": _GRANT_ID} for calendar_id in calendar_ids]),
    )


def _read_events():
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_read_skips_calendar_returning_404_and_emits_events_from_other_calendars(self, http_mocker: HttpMocker) -> None:
        """A subscribed calendar (e.g. a public holidays calendar) is listed by the calendars endpoint
        but the events endpoint answers 404 for it. The sync must skip it instead of failing the stream."""
        _given_grant_with_calendars(http_mocker, ["cal_primary", "cal_holidays", "cal_work"])
        http_mocker.get(
            _events_request("cal_primary"),
            _response([{"id": "evt_1", "calendar_id": "cal_primary", "grant_id": _GRANT_ID, "updated_at": 1788300000}]),
        )
        http_mocker.get(
            _events_request("cal_holidays"),
            HttpResponse(
                body=json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(
            _events_request("cal_work"),
            _response([{"id": "evt_2", "calendar_id": "cal_work", "grant_id": _GRANT_ID, "updated_at": 1788300100}]),
        )

        output = _read_events()

        assert sorted(record.record.data["id"] for record in output.records) == ["evt_1", "evt_2"]
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any("calendar" in log.log.message and "404" in log.log.message for log in output.logs)
