# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `booking` stream on `source-waiteraid`.

`POST /wa-api/searchBooking` answers with an envelope, `{"status": "OK", "bookings": [...]}`.
The stream must emit one record per entry of `bookings`, not the envelope itself.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_STREAM_NAME = "booking"
_URL = "https://app.waiteraid.com/wa-api/searchBooking"


def _booking(booking_id: int, date: str, amount: int) -> Dict[str, Any]:
    return {
        "id": booking_id,
        "date": date,
        "time": "19:00",
        "amount": amount,
        "status": "confirmed",
        "guest": {"id": booking_id * 10, "firstname": "Ada", "lastname": "Lovelace", "email": "ada@example.com"},
    }


def _search_booking_request(config: Dict[str, Any]) -> HttpRequest:
    return HttpRequest(
        url=_URL,
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )


def _search_booking_response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


def _read(config: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().build()
        bookings = [_booking(9001, "2026-09-03", 2), _booking(9002, "2026-09-04", 4)]
        http_mocker.post(_search_booking_request(config), _search_booking_response(bookings))

        output = _read(config)

        assert [record.record.data for record in output.records] == bookings
        assert not output.errors

    @HttpMocker()
    def test_read_emits_no_records_when_there_are_no_bookings(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().build()
        http_mocker.post(_search_booking_request(config), _search_booking_response([]))

        output = _read(config)

        assert output.records == []
        assert not output.errors
