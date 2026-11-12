# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    "response_body, expected_bookings",
    [
        pytest.param(
            {
                "status": "OK",
                "bookings": [
                    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101}},
                    {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102}},
                ],
            },
            [(9001, "2026-09-03", 2), (9002, "2026-09-03", 4)],
            id="multiple-bookings",
        ),
        pytest.param({"status": "OK", "bookings": []}, [], id="empty-bookings"),
        pytest.param({"status": "OK"}, [], id="missing-bookings"),
    ],
)
def test_booking_read(response_body, expected_bookings):
    config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps(response_body), status_code=200))
        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        records = [message.record.data for message in output.records]
        assert [record.get("id") for record in records] == [booking[0] for booking in expected_bookings]
        assert [(record["id"], record["date"], record["amount"]) for record in records] == expected_bookings
        http_mocker.assert_number_of_calls(request, 1)
