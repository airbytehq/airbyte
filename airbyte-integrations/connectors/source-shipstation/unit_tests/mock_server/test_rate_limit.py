# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import json_response, read_stream, request


@pytest.mark.parametrize(
    "stream_name, path, query_params, record",
    [
        ("tags", "accounts/listtags", None, {"tagId": 1, "name": "Fragile"}),
        ("carrier_packages", "carriers/listpackages", {"carrierCode": "ups"}, {"carrierCode": "ups", "code": "package"}),
        ("carrier_services", "carriers/listservices", {"carrierCode": "ups"}, {"carrierCode": "ups", "code": "ups_ground"}),
    ],
)
def test_429_waits_for_rate_limit_reset_header_then_reads_records(stream_name, path, query_params, record) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(request("carriers"), json_response([{"shippingProviderId": 1, "code": "ups"}]))
        http_request = request(path, query_params)
        http_mocker.get(
            http_request,
            [
                json_response({"message": "Too Many Requests"}, status_code=429, headers={"X-Rate-Limit-Reset": "7"}),
                json_response([record]),
            ],
        )

        with patch("time.sleep") as mocked_sleep:
            output = read_stream(stream_name)

        assert [r.record.data["code" if "code" in record else "tagId"] for r in output.records] == [record.get("code", record.get("tagId"))]
        assert output.errors == []
        http_mocker.assert_number_of_calls(http_request, 2)
        assert any(call.args and call.args[0] == pytest.approx(7, abs=1) for call in mocked_sleep.call_args_list)
