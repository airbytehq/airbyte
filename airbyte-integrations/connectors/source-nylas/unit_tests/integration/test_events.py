# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
_CONFIG = {
    "api_key": "fake",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_START = "1788220800"
_END = "1788393600"
_GRANTS_REQUEST = HttpRequest(
    "https://api.us.nylas.com/v3/grants",
    query_params={"limit": "50"},
)
_CALENDARS_REQUEST = HttpRequest(
    "https://api.us.nylas.com/v3/grants/grant-1/calendars",
    query_params={"limit": "50"},
)

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = _catalog()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=_CONFIG, state=state)
    return entrypoint_read(source, _CONFIG, catalog, state, expecting_exception)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        "https://api.us.nylas.com/v3/grants/grant-1/events",
        query_params={
            "limit": "50",
            "calendar_id": calendar_id,
            "start": _START,
            "end": _END,
        },
    )


def _mock_parents(http_mocker: HttpMocker) -> None:
    http_mocker.get(_GRANTS_REQUEST, HttpResponse(json.dumps({"data": [{"id": "grant-1"}]}), 200))
    http_mocker.get(
        _CALENDARS_REQUEST,
        HttpResponse(json.dumps({"data": [{"id": "primary-cal"}, {"id": "holidays-cal"}]}), 200),
    )


def test_events_skips_calendar_returning_404() -> None:
    primary_request = _events_request("primary-cal")
    holidays_request = _events_request("holidays-cal")

    with HttpMocker() as http_mocker:
        _mock_parents(http_mocker)
        http_mocker.get(
            holidays_request,
            HttpResponse(
                json.dumps({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}),
                404,
            ),
        )
        http_mocker.get(
            primary_request,
            HttpResponse(
                json.dumps(
                    {
                        "data": [
                            {
                                "id": "event-1",
                                "calendar_id": "primary-cal",
                                "grant_id": "grant-1",
                                "updated_at": 1788307200,
                            }
                        ]
                    }
                ),
                200,
            ),
        )

        output = _read(expecting_exception=True)

        http_mocker.assert_number_of_calls(holidays_request, 1)
        http_mocker.assert_number_of_calls(primary_request, 1)

    assert [record.record.data["id"] for record in output.records] == ["event-1"]
    assert not output.errors
    assert not any(error.trace.type.value == "ERROR" for error in output.errors)


def test_events_non_404_error_still_fails() -> None:
    holidays_request = _events_request("holidays-cal")
    primary_request = _events_request("primary-cal")

    with HttpMocker() as http_mocker:
        _mock_parents(http_mocker)
        http_mocker.get(
            holidays_request,
            HttpResponse(
                json.dumps({"request_id": "request-2", "error": {"type": "general", "message": "Forbidden"}}),
                403,
            ),
        )
        http_mocker.get(
            primary_request,
            HttpResponse(json.dumps({"data": []}), 200),
        )

        output = _read(expecting_exception=True)

        http_mocker.assert_number_of_calls(holidays_request, 1)
        http_mocker.assert_number_of_calls(primary_request, 1)

    assert output.errors
    assert any(error.trace.type.value == "ERROR" for error in output.errors)
