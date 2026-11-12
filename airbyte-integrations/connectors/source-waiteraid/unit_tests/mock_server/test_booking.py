# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `booking` stream on `source-waiteraid`.

`POST /wa-api/searchBooking` answers with an envelope, `{"status": "OK", "bookings": [...]}`.
The stream must emit one record per entry of `bookings`, not the envelope itself.
"""

import json
from typing import Any, Dict, List

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "booking"
_CONFIG = {"auth_hash": "test_auth_hash", "restid": "1234", "start_date": "2026-09-01"}


def _booking(booking_id: int, date: str, amount: int) -> Dict[str, Any]:
    return {
        "id": booking_id,
        "date": date,
        "amount": amount,
        "guest": {"id": booking_id + 100, "firstname": "Ada", "lastname": "Lovelace"},
    }


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test_auth_hash", "restid": "1234"},
    )


def _search_booking_response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


def _read(bookings: List[Dict[str, Any]]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(_search_booking_request(), _search_booking_response(bookings))
        return read(get_source(_CONFIG), _CONFIG, catalog)


def test_read_emits_one_record_per_booking() -> None:
    bookings = [_booking(9001, "2026-09-03", 2), _booking(9002, "2026-09-04", 5)]

    output = _read(bookings)

    assert [record.record.data for record in output.records] == bookings
    assert not output.errors


def test_read_emits_no_records_when_there_are_no_bookings() -> None:
    output = _read([])

    assert output.records == []
    assert not output.errors
