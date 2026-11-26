# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.parity_cases import CASES, SUBSTREAMS, payload
from mock_server.request_builder import BambooHrRequestBuilder
from mock_server.response_builder import response


@pytest.mark.parametrize("stream,path,record", CASES)
@pytest.mark.parametrize("empty", [False, True])
def test_full_refresh_records_and_requests(stream: str, path: str, record: dict[str, Any], empty: bool, http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    requests = []
    expected = []
    if stream in SUBSTREAMS:
        parent = BambooHrRequestBuilder("employees/directory").build()
        http_mocker.get(parent, response({"employees": [{"id": "1"}, {"id": "2"}]}))
        requests.append(parent)
    for parent_id in ["1", "2"] if stream in SUBSTREAMS else ["1"]:
        request = BambooHrRequestBuilder(path.replace("/1", f"/{parent_id}"))
        if stream == "goals":
            request.with_query_param("filter", "status-all")
        request = request.build()
        child = dict(record)
        id_field = "timeOffPolicyId" if stream == "employee_time_off_policies" else "id"
        if parent_id == "2" and stream == "employee_trainings":
            child["id"] = 12
            child["employeeId"] = parent_id
        http_mocker.get(request, response(payload(stream, [] if empty else [child])))
        requests.append(request)
        if not empty:
            if stream in SUBSTREAMS:
                child["employee_id" if stream == "goals" else "employeeId"] = parent_id
            expected.append(child)
    output = read(get_source(config), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())
    assert output.errors == []
    emitted = [message.record.data for message in output.records]
    assert len(emitted) == len(expected)
    for actual in emitted:
        assert any(all(actual.get(key) == value for key, value in item.items()) for item in expected)
    assert sorted((item[id_field], item.get("employee_id", item.get("employeeId"))) for item in emitted) == sorted(
        (item[id_field], item.get("employee_id", item.get("employeeId"))) for item in expected
    )
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    "terminal_url", [None, "https://api.bamboohr.com/api/gateway.php/test-company/v1/applicant_tracking/applications?page=3"]
)
def test_job_applications_follows_next_url_and_stops_when_complete(terminal_url: str | None, http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    path = "applicant_tracking/applications"
    first = BambooHrRequestBuilder(path).build()
    second = BambooHrRequestBuilder(path).with_query_param("page", "2").build()
    next_url = "https://api.bamboohr.com/api/gateway.php/test-company/v1/applicant_tracking/applications?page=2"
    http_mocker.get(first, response({"applications": [{"id": 11}], "paginationComplete": False, "nextPageUrl": next_url}))
    http_mocker.get(second, response({"applications": [{"id": 12}], "paginationComplete": True, "nextPageUrl": terminal_url}))
    output = read(get_source(config), config, CatalogBuilder().with_stream("job_applications", SyncMode.full_refresh).build())
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [11, 12]
    http_mocker.assert_number_of_calls(first, 1)
    http_mocker.assert_number_of_calls(second, 1)
