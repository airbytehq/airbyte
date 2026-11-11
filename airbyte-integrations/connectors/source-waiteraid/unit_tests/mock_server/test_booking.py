# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-auth-hash", "restid": "123", "start_date": "2026-11-01"}
BOOKINGS = [
    {"id": 9001, "date": "2026-11-01", "amount": 2, "guest": {"id": 101, "name": "Ada Lovelace"}},
    {"id": 9002, "date": "2026-11-02", "amount": 4, "guest": {"id": 102, "name": "Grace Hopper"}},
]


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["multiple_bookings", "empty_bookings"])
def test_booking_records(bookings: list[dict]) -> None:
    request = HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"], "date": CONFIG["start_date"]},
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    with HttpMocker() as mocker:
        mocker.post(request, HttpResponse(json.dumps({"status": "OK", "bookings": bookings})))

        output = read(get_source(CONFIG, catalog), config=CONFIG, catalog=catalog)

        assert output.errors == []
        records = [message.record.data for message in output.records]
        assert records == bookings
        assert [record["id"] for record in records] == [booking["id"] for booking in bookings]
        assert all("status" not in record and "bookings" not in record for record in records)
        mocker.assert_number_of_calls(request, 1)
