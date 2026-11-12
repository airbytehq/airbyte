# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_USER_ID = "test_user_id"
_CONFIG = {
    "api_key": "test_api_key",
    "user_id": _USER_ID,
    "start_date": "2026-01-01T00:00:00Z",
}
_BASE_URL = f"https://api.clarifai.com/v2/users/{_USER_ID}/apps"

# Clarifai serializes timestamps with nanosecond precision and drops the fraction when it is zero.
_NANOSECOND_OLDER = "2026-10-02T17:05:11.904417302Z"
_NANOSECOND_NEWEST = "2026-10-14T09:41:55.568082659Z"
_WHOLE_SECOND = "2026-09-01T08:00:00Z"
_NEWEST_AS_STATE = "2026-10-14T09:41:55.568082Z"


def _apps_request() -> HttpRequest:
    return HttpRequest(url=_BASE_URL, query_params={"page": "1", "per_page": "20"})


def _substream_request(app_id: str, stream_name: str) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}/{app_id}/{stream_name}", query_params={"page": "1", "per_page": "100"})


def _response(field: str, records: list) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": {"code": 10000, "description": "Ok"}, field: records}), status_code=200)


def _read(stream_name: str, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _final_state(output) -> dict:
    return output.most_recent_state.stream_state.__dict__


def test_applications_state_advances_to_newest_modified_at():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _apps_request(),
            _response(
                "apps",
                [
                    {"id": "app_whole_second", "modified_at": _WHOLE_SECOND},
                    {"id": "app_newest", "modified_at": _NANOSECOND_NEWEST},
                    {"id": "app_older", "modified_at": _NANOSECOND_OLDER},
                ],
            ),
        )

        output = _read("applications")

        assert [(record.record.data["id"], record.record.data["modified_at"]) for record in output.records] == [
            ("app_whole_second", _WHOLE_SECOND),
            ("app_newest", _NEWEST_AS_STATE),
            ("app_older", "2026-10-02T17:05:11.904417Z"),
        ]
        assert _final_state(output) == {"modified_at": _NEWEST_AS_STATE}
        assert not any("failed to parse cursor field" in log.log.message for log in output.logs)


def test_applications_state_advances_for_whole_second_modified_at():
    with HttpMocker() as http_mocker:
        http_mocker.get(_apps_request(), _response("apps", [{"id": "app_whole_second", "modified_at": _WHOLE_SECOND}]))

        output = _read("applications")

        assert [record.record.data["id"] for record in output.records] == ["app_whole_second"]
        assert _final_state(output) == {"modified_at": "2026-09-01T08:00:00.000000Z"}


def test_applications_second_sync_carries_state_forward():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _apps_request(),
            _response(
                "apps",
                [
                    {"id": "app_unchanged", "modified_at": _NANOSECOND_OLDER},
                    {"id": "app_edited", "modified_at": "2026-11-03T12:30:45.123456789Z"},
                ],
            ),
        )
        state = StateBuilder().with_stream_state("applications", {"modified_at": _NEWEST_AS_STATE}).build()

        output = _read("applications", state)

        # The API has no modified-since filter, so every sync requests and emits the full list.
        assert [record.record.data["id"] for record in output.records] == ["app_unchanged", "app_edited"]
        assert _final_state(output) == {"modified_at": "2026-11-03T12:30:45.123456Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_state_advances_per_app(stream_name: str):
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _apps_request(),
            _response(
                "apps",
                [
                    {"id": "app_1", "modified_at": _NANOSECOND_OLDER},
                    {"id": "app_2", "modified_at": _NANOSECOND_OLDER},
                ],
            ),
        )
        http_mocker.get(
            _substream_request("app_1", stream_name),
            _response(
                stream_name,
                [
                    {"id": "app_1_older", "modified_at": _NANOSECOND_OLDER},
                    {"id": "app_1_newest", "modified_at": _NANOSECOND_NEWEST},
                ],
            ),
        )
        http_mocker.get(
            _substream_request("app_2", stream_name),
            _response(stream_name, [{"id": "app_2_only", "modified_at": _NANOSECOND_OLDER}]),
        )

        output = _read(stream_name)

        assert sorted(record.record.data["id"] for record in output.records) == ["app_1_newest", "app_1_older", "app_2_only"]
        cursor_by_app = {partition["partition"]["app_id"]: partition["cursor"] for partition in _final_state(output)["states"]}
        assert cursor_by_app == {
            "app_1": {"modified_at": _NEWEST_AS_STATE},
            "app_2": {"modified_at": "2026-10-02T17:05:11.904417Z"},
        }
