# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "booking"
_BOOKING_REQUEST = HttpRequest(
    "https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-09-01", "auth_hash": "hash", "restid": "1234"},
)
_CONFIG = {"auth_hash": "hash", "restid": "1234", "start_date": "2026-09-01"}


def _read_bookings() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class BookingStreamTest(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking(self, http_mocker: HttpMocker):
        bookings = [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"firstname": "A"}},
            {"id": 9002, "date": "2026-09-04", "amount": 3, "guest": {"firstname": "B"}},
        ]
        http_mocker.post(
            _BOOKING_REQUEST,
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )

        output = _read_bookings()

        assert output.errors == []
        assert len(output.records) == 2
        assert [record.record.data["id"] for record in output.records] == [9001, 9002]
        assert [record.record.data["date"] for record in output.records] == ["2026-09-03", "2026-09-04"]
        assert [record.record.data["amount"] for record in output.records] == [2, 3]
        for record in output.records:
            assert "bookings" not in record.record.data
            assert "status" not in record.record.data
        http_mocker.assert_number_of_calls(_BOOKING_REQUEST, 1)

    @HttpMocker()
    def test_read_empty_bookings_emits_no_records(self, http_mocker: HttpMocker):
        http_mocker.post(
            _BOOKING_REQUEST,
            HttpResponse(body=json.dumps({"status": "OK", "bookings": []}), status_code=200),
        )

        output = _read_bookings()

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(_BOOKING_REQUEST, 1)
