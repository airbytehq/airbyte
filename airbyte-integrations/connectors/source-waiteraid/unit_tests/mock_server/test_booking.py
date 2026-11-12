# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_STREAM_NAME = "booking"
_CONFIG = {"auth_hash": "test_auth_hash", "restid": "1234", "start_date": "2026-09-01"}

_SEARCH_BOOKING_REQUEST = HttpRequest(
    url="https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-09-01", "auth_hash": "test_auth_hash", "restid": "1234"},
)

_BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "confirmed", "guest": {"id": 501, "firstname": "Ada"}},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "confirmed", "guest": {"id": 502, "firstname": "Grace"}},
    {"id": 9003, "date": "2026-09-05", "amount": 6, "status": "cancelled", "guest": {"id": 503, "firstname": "Edsger"}},
]


def _read(response_body: dict):
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(_SEARCH_BOOKING_REQUEST, HttpResponse(body=json.dumps(response_body), status_code=200))
        return read(get_source(_CONFIG), _CONFIG, catalog)


def test_full_refresh_emits_one_record_per_booking():
    """The API wraps bookings in {"status": ..., "bookings": [...]}; each booking must be its own record."""
    output = _read({"status": "OK", "bookings": _BOOKINGS})

    assert [record.record.data for record in output.records] == _BOOKINGS
    assert not output.errors


def test_full_refresh_emits_no_records_when_there_are_no_bookings():
    """An empty bookings list must not surface the response envelope as a record."""
    output = _read({"status": "OK", "bookings": []})

    assert output.records == []
    assert not output.errors
