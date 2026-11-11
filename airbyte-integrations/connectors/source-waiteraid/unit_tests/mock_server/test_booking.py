# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-auth-hash", "restid": "123", "start_date": "2026-09-03"}
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Alice"}},
    {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "name": "Bob"}},
]


def booking_request() -> HttpRequest:
    return HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["two-bookings", "empty"])
def test_booking_read(http_mocker: HttpMocker, bookings: list[dict]) -> None:
    request = booking_request()
    http_mocker.post(request, HttpResponse(json.dumps({"status": "OK", "bookings": bookings}), 200))
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    output = read(get_source(CONFIG), CONFIG, catalog)

    assert not output.errors
    records = [message.record.data for message in output.records]
    assert [record.get("id") for record in records] == [booking["id"] for booking in bookings]
    assert all("bookings" not in record and record.get("status") != "OK" for record in records)
    assert records == bookings
    http_mocker.assert_number_of_calls(request, 1)


def test_booking_read_authentication_error(http_mocker: HttpMocker) -> None:
    request = booking_request()
    http_mocker.post(request, HttpResponse(json.dumps({"status": "ERROR"}), 401))
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    output = read(get_source(CONFIG), CONFIG, catalog, expecting_exception=True)

    assert output.errors
    assert not output.records
    http_mocker.assert_number_of_calls(request, 1)
