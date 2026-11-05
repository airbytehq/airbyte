# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "42"}
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Alice"}},
    {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "name": "Bob"}},
]


def booking_request():
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["multiple_bookings", "empty_bookings"])
def test_read_booking(bookings):
    request = booking_request()
    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))
        output = read(
            get_source(CONFIG),
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build(),
        )
        http_mocker.assert_number_of_calls(request, 1)

    records = [message.record.data for message in output.records]
    assert len(records) == len(bookings)
    assert [record["id"] for record in records] == [booking["id"] for booking in bookings]
    assert records == bookings
    assert all("status" not in record for record in records)
    assert not output.errors

