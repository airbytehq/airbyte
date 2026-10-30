# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the upper bound of the incremental date window.

`end_date` used to be a required spec field, so every incremental sync was capped at a
fixed date and new events, messages, threads and drafts stopped syncing once that date
passed. `end_date` is now optional: when it is omitted the window ends at the current
time, and when it is set it still caps the window.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

from freezegun import freeze_time
from unit_tests.conftest import _YAML_FILE_PATH, get_source

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_NOW = "2026-10-30T12:00:00Z"
_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_CALENDAR_ID = "calendar-1"
_START_DATE = "2026-09-01T00:00:00Z"
_END_DATE = "2026-09-15T00:00:00Z"


def _timestamp(value: str) -> str:
    return str(int(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()))


def _config(end_date: Optional[str] = None) -> Dict[str, Any]:
    config = {"api_key": "key", "api_server": "us", "start_date": _START_DATE}
    if end_date:
        config["end_date"] = end_date
    return config


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _mock_grants(http_mocker: HttpMocker) -> None:
    http_mocker.get(HttpRequest(f"{_BASE_URL}/grants", query_params={"limit": "50"}), _page([{"id": _GRANT_ID}]))


def _read(stream_name: str, config: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(config=config), config=config, catalog=catalog)


class SpecTest(TestCase):
    def test_end_date_is_optional(self) -> None:
        spec = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]["connection_specification"]
        assert "end_date" not in spec["required"]
        assert "start_date" in spec["required"]


@freeze_time(_NOW)
class EventsEndDateTest(TestCase):
    def _mock_calendars(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
            _page([{"id": _CALENDAR_ID, "grant_id": _GRANT_ID}]),
        )

    @HttpMocker()
    def test_window_ends_now_when_end_date_is_omitted(self, http_mocker: HttpMocker) -> None:
        _mock_grants(http_mocker)
        self._mock_calendars(http_mocker)
        http_mocker.get(
            HttpRequest(
                f"{_BASE_URL}/grants/{_GRANT_ID}/events",
                query_params={
                    "limit": "50",
                    "calendar_id": _CALENDAR_ID,
                    "start": _timestamp(_START_DATE),
                    "end": _timestamp(_NOW),
                },
            ),
            _page([{"id": "event-october", "calendar_id": _CALENDAR_ID, "updated_at": int(_timestamp("2026-10-20T09:00:00Z"))}]),
        )

        output = _read("events", _config())

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["event-october"]

    @HttpMocker()
    def test_window_is_capped_by_end_date_when_set(self, http_mocker: HttpMocker) -> None:
        _mock_grants(http_mocker)
        self._mock_calendars(http_mocker)
        http_mocker.get(
            HttpRequest(
                f"{_BASE_URL}/grants/{_GRANT_ID}/events",
                query_params={
                    "limit": "50",
                    "calendar_id": _CALENDAR_ID,
                    "start": _timestamp(_START_DATE),
                    "end": _timestamp(_END_DATE),
                },
            ),
            _page([{"id": "event-september", "calendar_id": _CALENDAR_ID, "updated_at": int(_timestamp("2026-09-10T09:00:00Z"))}]),
        )

        output = _read("events", _config(end_date=_END_DATE))

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["event-september"]


@freeze_time(_NOW)
class MessagesEndDateTest(TestCase):
    @HttpMocker()
    def test_window_ends_now_when_end_date_is_omitted(self, http_mocker: HttpMocker) -> None:
        _mock_grants(http_mocker)
        http_mocker.get(
            HttpRequest(
                f"{_BASE_URL}/grants/{_GRANT_ID}/messages",
                query_params={
                    "limit": "50",
                    "received_after": _timestamp(_START_DATE),
                    "received_before": _timestamp(_NOW),
                },
            ),
            _page([{"id": "message-october", "grant_id": _GRANT_ID, "date": int(_timestamp("2026-10-20T09:00:00Z"))}]),
        )

        output = _read("messages", _config())

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["message-october"]
