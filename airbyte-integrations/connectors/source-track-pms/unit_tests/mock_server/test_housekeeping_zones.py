# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import read_stream, request, response


LINKS = {"_links": {"self": {"href": "ignored"}}}


@pytest.mark.parametrize("scenario", ["paginated", "empty", "invalid_page"])
def test_housekeeping_zones(scenario: str) -> None:
    path = "pms/housekeeping/zones"
    with HttpMocker() as http_mocker:
        if scenario == "paginated":
            http_mocker.get(request(path), response("zones", [{"id": i, "name": f"Zone {i}", **LINKS} for i in range(1, 101)]))
            http_mocker.get(request(path, 2), response("zones", [{"id": 101, **LINKS}], page=2))
        elif scenario == "empty":
            http_mocker.get(request(path), response("zones", []))
        else:
            http_mocker.get(request(path), response("zones", [{"id": i, **LINKS} for i in range(1, 101)]))
            http_mocker.get(request(path, 2), HttpResponse('{"status": 409, "detail": "Invalid page provided"}', status_code=409))

        output = read_stream("housekeeping_zones")

        last_id = {"paginated": 101, "empty": 0, "invalid_page": 100}[scenario]
        assert {r.record.data["id"] for r in output.records} == set(range(1, last_id + 1))
        assert len(output.records) == last_id
        assert all("_links" not in r.record.data for r in output.records)
        http_mocker.assert_number_of_calls(request(path), 1)
        if scenario != "empty":
            http_mocker.assert_number_of_calls(request(path, 2), 1)
        assert not any(log.log.level == "ERROR" for log in output.logs)
