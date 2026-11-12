# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `booking` stream on `source-waiteraid`.

`POST /wa-api/searchBooking` returns the bookings wrapped in an envelope:
`{"status": "OK", "bookings": [...]}`.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


_STREAM_NAME = "booking"
_URL = "https://app.waiteraid.com/wa-api/searchBooking"


def _request() -> HttpRequest:
    return HttpRequest(url=_URL, query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"})


def _response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


def _booking(booking_id: int, **overrides) -> Dict[str, Any]:
    booking = {
        "id": booking_id,
        "date": "2026-09-03",
        "time": "19:00",
        "amount": 2,
        "status": "confirmed",
        "guest": {"id": booking_id + 100, "firstname": "Ada", "lastname": "Lovelace", "email": "ada@example.com"},
    }
    booking.update(overrides)
    return booking


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestBooking(TestCase):
    @HttpMocker()
    def test_emits_one_record_per_booking_in_the_response_envelope(self, http_mocker: HttpMocker):
        """Each entry of the `bookings` array becomes its own record with the booking fields at the top level."""
        bookings = [_booking(9001), _booking(9002, date="2026-09-04", amount=4), _booking(9003, date="2026-09-05", amount=6)]
        http_mocker.post(_request(), _response(bookings))

        output = _read()

        assert [record.record.data for record in output.records] == bookings
        assert output.errors == []

    @HttpMocker()
    def test_emits_no_records_when_the_bookings_array_is_empty(self, http_mocker: HttpMocker):
        """An envelope with no bookings yields no records rather than a row holding the envelope."""
        http_mocker.post(_request(), _response([]))

        output = _read()

        assert output.records == []
        assert output.errors == []
