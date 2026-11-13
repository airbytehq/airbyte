# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import read_stream, request, response


@pytest.mark.parametrize(
    "stream,parent_path,parent_key,partition_key,child_path",
    [
        ("units_daily_pricing_v2", "pms/units", "units", "unit_id", "v2/pms/units"),
        ("units_types_daily_pricing_v2", "pms/units/types", "unitTypes", "unit_type_id", "v2/pms/units/types"),
    ],
)
@pytest.mark.parametrize("child_status", [200, 404])
def test_all_parents_get_daily_pricing(
    stream: str, parent_path: str, parent_key: str, partition_key: str, child_path: str, child_status: int
) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(request(parent_path), response(parent_key, [{"id": 1, "lodgingTypeId": 5}, {"id": 2, "lodgingTypeId": None}]))
        for parent_id in (1, 2):
            body = [{"rateTypeId": parent_id, "rates": []}] if child_status == 200 else {"status": 404}
            http_mocker.get(request(f"{child_path}/{parent_id}/daily-pricing"), HttpResponse(json.dumps(body), status_code=child_status))

        output = read_stream(stream)

        assert {(r.record.data[partition_key], r.record.data["rateTypeId"]) for r in output.records} == (
            {(1, 1), (2, 2)} if child_status == 200 else set()
        )
        assert len(output.records) == (2 if child_status == 200 else 0)
        for parent_id in (1, 2):
            http_mocker.assert_number_of_calls(request(f"{child_path}/{parent_id}/daily-pricing"), 1)
        assert not any(log.log.level == "ERROR" for log in output.logs)
