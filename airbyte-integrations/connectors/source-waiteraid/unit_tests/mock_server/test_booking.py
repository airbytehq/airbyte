# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"},
    )


def _booking(booking_id: int, date: str, amount: int, status: str) -> dict:
    return {
        "id": booking_id,
        "date": date,
        "amount": amount,
        "status": status,
        "guest": {"id": booking_id * 10, "firstname": "Ada", "lastname": "Lovelace"},
    }


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_full_refresh_emits_one_record_per_booking(self, http_mocker: HttpMocker) -> None:
        bookings = [
            _booking(9001, "2026-09-03", 2, "confirmed"),
            _booking(9002, "2026-09-04", 4, "arrived"),
        ]
        http_mocker.post(
            _search_booking_request(),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert [record.record.data for record in output.records] == bookings
        assert [record.record.data["id"] for record in output.records] == [9001, 9002]
        assert all("bookings" not in record.record.data for record in output.records)

    @HttpMocker()
    def test_full_refresh_with_no_bookings_emits_no_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            _search_booking_request(),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": []}), status_code=200),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
