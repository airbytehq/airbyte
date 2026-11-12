# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}

_BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "confirmed", "guest": {"id": 501, "firstname": "Ada"}},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "cancelled", "guest": {"id": 502, "firstname": "Grace"}},
]


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"},
    )


def _read_booking(response_body: str):
    with HttpMocker() as http_mocker:
        http_mocker.post(_search_booking_request(), HttpResponse(body=response_body, status_code=200))
        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        return read(get_source(_CONFIG), _CONFIG, catalog)


def test_booking_read_emits_one_record_per_booking():
    """The API wraps bookings in `{"status": ..., "bookings": [...]}`; each booking must become its own record."""
    output = _read_booking(json.dumps({"status": "OK", "bookings": _BOOKINGS}))

    assert [record.record.data for record in output.records] == _BOOKINGS


def test_booking_read_emits_no_records_when_there_are_no_bookings():
    output = _read_booking('{"status": "OK", "bookings": []}')

    assert output.records == []
    assert not any(log.log.level == "ERROR" for log in output.logs)
