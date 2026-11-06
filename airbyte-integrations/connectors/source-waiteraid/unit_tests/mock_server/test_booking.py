# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


@pytest.mark.parametrize("booking_ids", [[9001, 9002], []], ids=["bookings", "empty"])
def test_read_booking(booking_ids):
    config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}
    bookings = [
        {"id": booking_id, "date": config["start_date"], "amount": 2, "guest": {"id": booking_id + 100}} for booking_id in booking_ids
    ]
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data.get("id") for message in output.records] == booking_ids
        http_mocker.assert_number_of_calls(request, 1)
