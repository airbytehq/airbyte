# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `booking` stream.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "booking"
_BOOKINGS_URL = "https://app.waiteraid.com/wa-api/searchBooking"

_CONFIG = {
    "auth_hash": "hash",
    "restid": "1234",
    "start_date": "2026-09-01",
}

_BOOKINGS_REQUEST = HttpRequest(
    _BOOKINGS_URL,
    query_params={"date": "2026-09-01", "auth_hash": "hash", "restid": "1234"},
)


def _booking(booking_id: int, guest_id: int, guest_name: str, amount: int) -> Dict[str, Any]:
    return {
        "id": booking_id,
        "date": "2026-09-03",
        "amount": amount,
        "guest": {"id": guest_id, "name": guest_name},
    }


def _bookings_response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


def _read_bookings() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class BookingStreamTest(TestCase):
    @HttpMocker()
    def test_booking_stream_emits_one_record_per_booking(self, http_mocker: HttpMocker):
        http_mocker.post(
            _BOOKINGS_REQUEST,
            _bookings_response(
                [
                    _booking(9001, 101, "Ada Guest", 2),
                    _booking(9002, 102, "Bert Guest", 3),
                    _booking(9003, 103, "Cam Guest", 4),
                ]
            ),
        )

        output = _read_bookings()

        assert output.errors == []
        records = [record.record.data for record in output.records]
        assert len(records) == 3, records
        assert [record["id"] for record in records] == [9001, 9002, 9003]
        assert records[0]["date"] == "2026-09-03"
        assert records[0]["amount"] == 2
        assert records[0]["guest"] == {"id": 101, "name": "Ada Guest"}
        for record in records:
            assert "bookings" not in record
            assert record.get("status") != "OK"

    @HttpMocker()
    def test_booking_stream_empty_bookings_emits_no_records(self, http_mocker: HttpMocker):
        http_mocker.post(_BOOKINGS_REQUEST, _bookings_response([]))

        output = _read_bookings()

        assert output.errors == []
        assert output.records == []
