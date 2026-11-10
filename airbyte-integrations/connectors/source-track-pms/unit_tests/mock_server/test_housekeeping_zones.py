# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import read_stream, request, response


@pytest.mark.parametrize("scenario", ["paginated", "empty", "invalid_page"])
def test_housekeeping_zones(scenario: str) -> None:
    path = "pms/housekeeping/zones"
    with HttpMocker() as http_mocker:
        if scenario == "paginated":
            http_mocker.get(request(path), response("zones", [{"id": str(i), "name": f"Zone {i}"} for i in range(1, 101)]))
            http_mocker.get(request(path, 2), response("zones", [{"id": "101"}], page=2))
        elif scenario == "empty":
            http_mocker.get(request(path), response("zones", []))
        else:
            http_mocker.get(request(path), HttpResponse('{"status": 409, "detail": "Invalid page provided"}', status_code=409))

        output = read_stream("housekeeping_zones")

        assert {r.record.data["id"] for r in output.records} == ({str(i) for i in range(1, 102)} if scenario == "paginated" else set())
        assert len(output.records) == (101 if scenario == "paginated" else 0)
        http_mocker.assert_number_of_calls(request(path), 1)
        if scenario == "paginated":
            http_mocker.assert_number_of_calls(request(path, 2), 1)
        assert not any(log.log.level == "ERROR" for log in output.logs)
