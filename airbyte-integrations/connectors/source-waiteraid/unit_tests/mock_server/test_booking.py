# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "booking"
_CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
_SEARCH_BOOKING_REQUEST = HttpRequest(
    url="https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"},
)
_SEARCH_BOOKING_RESPONSE = """
{
  "status": "OK",
  "bookings": [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "confirmed", "guest": {"id": 501, "firstname": "Ada"}},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "confirmed", "guest": {"id": 502, "firstname": "Linus"}}
  ]
}
"""


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_SEARCH_BOOKING_REQUEST, HttpResponse(body=_SEARCH_BOOKING_RESPONSE, status_code=200))

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert [record.record.data for record in output.records] == [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "confirmed", "guest": {"id": 501, "firstname": "Ada"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "confirmed", "guest": {"id": 502, "firstname": "Linus"}},
        ]
