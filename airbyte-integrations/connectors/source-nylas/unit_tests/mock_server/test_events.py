# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3/grants"
GRANT_ID = "grant-1"
START = "1788220800"
END = "1788393600"


def _page(records: list[dict]) -> HttpResponse:
    return HttpResponse(json.dumps({"request_id": "req", "data": records}))


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        f"{BASE_URL}/{GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": START, "end": END},
    )


def _read_events() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=None,
    )
    return read(source, config=CONFIG, catalog=catalog)


def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync(http_mocker: HttpMocker) -> None:
    http_mocker.get(HttpRequest(BASE_URL, query_params={"limit": "50"}), _page([{"id": GRANT_ID}]))
    http_mocker.get(
        HttpRequest(f"{BASE_URL}/{GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page([{"id": "holidays-calendar", "read_only": True}, {"id": "primary-calendar", "is_primary": True}]),
    )
    not_found = _events_request("holidays-calendar")
    found = _events_request("primary-calendar")
    http_mocker.get(
        not_found,
        HttpResponse(json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}), status_code=404),
    )
    http_mocker.get(found, _page([{"id": "event-1", "calendar_id": "primary-calendar", "updated_at": 1788300000}]))

    output = _read_events()

    assert output.errors == []
    assert not any(log.log.level == "ERROR" for log in output.logs)
    assert [record.record.data["id"] for record in output.records] == ["event-1"]
    http_mocker.assert_number_of_calls(not_found, 1)
    http_mocker.assert_number_of_calls(found, 1)
