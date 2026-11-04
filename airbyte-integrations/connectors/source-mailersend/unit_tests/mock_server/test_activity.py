# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


_STREAM_NAME = "activity"
_API_BASE_URL = "https://api.mailersend.com/v1"
_FROZEN_TIME = "2026-09-02T12:00:00Z"


def _activity_request(date_from: int, date_to: int, page: int | None = None) -> HttpRequest:
    query_params = {
        "limit": "100",
        "page_size": "100",
        "date_from": str(date_from),
        "date_to": str(date_to),
    }
    if page is not None:
        query_params["page"] = str(page)

    return HttpRequest(
        url=f"{_API_BASE_URL}/activity/example.com",
        query_params=query_params,
        headers={"Authorization": "Bearer test-api-token"},
    )


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": records}), status_code=200)


def _read(config: Dict[str, Any], state=None) -> EntrypointOutput:
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


@freezegun.freeze_time(_FROZEN_TIME)
def test_incremental_first_sync_sends_date_range_per_slice():
    config = ConfigBuilder().build()
    first_request = _activity_request(1788220800, 1788307199)
    second_request = _activity_request(1788307200, 1788350400)

    with HttpMocker() as http_mocker:
        http_mocker.get(
            first_request,
            _page([{"id": "activity-1", "created_at": "2026-09-01T09:30:00.000000Z"}]),
        )
        http_mocker.get(
            second_request,
            _page([{"id": "activity-2", "created_at": "2026-09-02T09:30:00.000000Z"}]),
        )
        output = _read(config)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["activity-1", "activity-2"]
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": "1788341400"}
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(second_request, 1)


@freezegun.freeze_time(_FROZEN_TIME)
def test_incremental_sync_resumes_from_state():
    config = ConfigBuilder().build()
    state = StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": "1788307200"}).build()
    request = _activity_request(1788307200, 1788350400)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page([{"id": "activity-2", "created_at": "2026-09-02T09:30:00.000000Z"}]))
        output = _read(config, state)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["activity-2"]
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": "1788341400"}
    http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(_FROZEN_TIME)
def test_incremental_paginates_with_exact_page_parameters():
    config = ConfigBuilder().with_start_date(1788346800).build()
    first_request = _activity_request(1788346800, 1788350400)
    second_request = _activity_request(1788346800, 1788350400, page=1)
    first_page = [{"id": f"activity-{i}", "created_at": "2026-09-02T11:10:00.000000Z"} for i in range(100)]

    with HttpMocker() as http_mocker:
        http_mocker.get(first_request, _page(first_page))
        http_mocker.get(second_request, _page([{"id": "activity-100", "created_at": "2026-09-02T11:30:00.000000Z"}]))
        output = _read(config)

    assert output.errors == []
    assert len(output.records) == 101
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": "1788348600"}
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(second_request, 1)
