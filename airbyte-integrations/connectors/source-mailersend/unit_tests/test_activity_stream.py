# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `activity` stream.

`GET /v1/activity/{domain_id}` requires both `date_from` and `date_to` (Unix
timestamps) and answers `422` when `date_to` is missing. Records carry ISO 8601
`created_at` values such as `2026-09-02T09:30:00.000000Z`. Pagination is
1-indexed through `page` with the page size sent as `limit`.
"""

import json
from typing import Any, Dict, List, Optional

from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_STREAM_NAME = "activity"
_DOMAIN_ID = "domain123"
_ACTIVITY_URL = f"https://api.mailersend.com/v1/activity/{_DOMAIN_ID}"

# 2026-09-01T00:00:00Z
_START_DATE = 1788220800
# 2026-09-03T12:00:00Z
_NOW = "2026-09-03T12:00:00Z"
_NOW_TIMESTAMP = 1788436800
_ONE_DAY = 86400

_CONFIG = {"api_token": "token", "domain_id": _DOMAIN_ID, "start_date": _START_DATE}


def _activity_request(date_from: int, date_to: int, page: Optional[int] = None) -> HttpRequest:
    query_params = {"date_from": str(date_from), "date_to": str(date_to), "limit": "100"}
    if page is not None:
        query_params["page"] = str(page)
    return HttpRequest(_ACTIVITY_URL, query_params=query_params)


def _activity(activity_id: str, created_at: str) -> Dict[str, Any]:
    return {
        "id": activity_id,
        "created_at": created_at,
        "updated_at": created_at,
        "type": "delivered",
        "email": {"id": f"email-{activity_id}", "from": "no-reply@example.com", "status": "delivered"},
    }


def _activity_response(activities: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": activities, "meta": {"per_page": 100}}), status_code=200)


def _read(sync_mode: SyncMode, state: Optional[List[Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
    return read(get_source(config=_CONFIG, state=state), config=_CONFIG, catalog=catalog, state=state)


@freeze_time(_NOW)
def test_activity_sends_date_range_per_daily_slice_and_paginates_from_page_two() -> None:
    with HttpMocker() as http_mocker:
        day_1_start = _START_DATE
        day_2_start = _START_DATE + _ONE_DAY
        day_3_start = _START_DATE + 2 * _ONE_DAY
        full_page = [_activity(f"a{i}", "2026-09-01T10:00:00.000000Z") for i in range(100)]

        http_mocker.get(_activity_request(day_1_start, day_2_start - 1), _activity_response(full_page))
        http_mocker.get(
            _activity_request(day_1_start, day_2_start - 1, page=2),
            _activity_response([_activity("a100", "2026-09-01T11:00:00.000000Z")]),
        )
        http_mocker.get(
            _activity_request(day_2_start, day_3_start - 1),
            _activity_response([_activity("b0", "2026-09-02T09:30:00.000000Z")]),
        )
        http_mocker.get(_activity_request(day_3_start, _NOW_TIMESTAMP), _activity_response([]))

        output = _read(SyncMode.full_refresh)

    assert output.errors == []
    assert len(output.records) == 102
    assert {record.record.data["id"] for record in output.records} == {f"a{i}" for i in range(101)} | {"b0"}


@freeze_time(_NOW)
def test_activity_incremental_emits_epoch_state_from_iso_created_at() -> None:
    with HttpMocker() as http_mocker:
        day_2_start = _START_DATE + _ONE_DAY
        day_3_start = _START_DATE + 2 * _ONE_DAY
        http_mocker.get(_activity_request(_START_DATE, day_2_start - 1), _activity_response([]))
        http_mocker.get(
            _activity_request(day_2_start, day_3_start - 1),
            _activity_response([_activity("b0", "2026-09-02T09:30:00.000000Z")]),
        )
        http_mocker.get(_activity_request(day_3_start, _NOW_TIMESTAMP), _activity_response([]))

        output = _read(SyncMode.incremental)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["b0"]
    # 2026-09-02T09:30:00Z
    assert output.most_recent_state.stream_state.__dict__["created_at"] == "1788341400"


@freeze_time(_NOW)
def test_activity_incremental_resumes_from_state() -> None:
    # 2026-09-02T09:30:00Z
    cursor = 1788341400
    state = StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": str(cursor)}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _activity_request(cursor, cursor + _ONE_DAY - 1),
            _activity_response([_activity("c0", "2026-09-02T18:00:00.000000Z")]),
        )
        http_mocker.get(_activity_request(cursor + _ONE_DAY, _NOW_TIMESTAMP), _activity_response([]))

        output = _read(SyncMode.incremental, state=state)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["c0"]
