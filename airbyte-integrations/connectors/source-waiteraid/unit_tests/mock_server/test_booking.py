# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_CONFIG = {
    "auth_hash": "test-auth-hash",
    "restid": "1234",
    "start_date": "2026-09-01",
}
_STREAM_NAME = "booking"


def _booking(booking_id: int, date: str, amount: int, guest_id: int) -> dict:
    return {
        "id": booking_id,
        "date": date,
        "amount": amount,
        "status": "confirmed",
        "guest": {"id": guest_id, "firstname": "Ada", "lastname": "Lovelace"},
    }


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking_in_response(self, http_mocker: HttpMocker) -> None:
        bookings = [
            _booking(9001, "2026-09-03", 2, 501),
            _booking(9002, "2026-09-04", 4, 502),
            _booking(9003, "2026-09-05", 1, 503),
        ]
        http_mocker.post(
            HttpRequest(
                url="https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"},
            ),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        records = [message.record.data for message in output.records]
        assert records == bookings
