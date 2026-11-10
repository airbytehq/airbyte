# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import json_response, read_stream, request


@pytest.mark.parametrize(
    "stream_name, path",
    [("carrier_packages", "carriers/listpackages"), ("carrier_services", "carriers/listservices")],
)
def test_reads_one_request_per_parent_carrier_and_keys_records_by_carrier(stream_name: str, path: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request("carriers"),
            json_response([{"shippingProviderId": 1, "code": "fedex"}, {"shippingProviderId": 2, "code": "ups"}]),
        )
        fedex_request = request(path, {"carrierCode": "fedex"})
        ups_request = request(path, {"carrierCode": "ups"})
        http_mocker.get(
            fedex_request,
            json_response(
                [
                    {"carrierCode": "fedex", "code": "fedex_ground", "name": "FedEx Ground", "domestic": True, "international": False},
                    {"carrierCode": "fedex", "code": "fedex_2day", "name": "FedEx 2Day", "domestic": True, "international": False},
                ]
            ),
        )
        # Records without carrierCode get it from the parent carrier so the [carrierCode, code] key stays populated.
        http_mocker.get(
            ups_request, json_response([{"code": "ups_ground", "name": "UPS Ground", "domestic": True, "international": False}])
        )

        output = read_stream(stream_name)

        assert sorted((r.record.data["carrierCode"], r.record.data["code"]) for r in output.records) == [
            ("fedex", "fedex_2day"),
            ("fedex", "fedex_ground"),
            ("ups", "ups_ground"),
        ]
        assert output.errors == []
        http_mocker.assert_number_of_calls(fedex_request, 1)
        http_mocker.assert_number_of_calls(ups_request, 1)
