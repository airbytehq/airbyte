# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `booking` stream on `source-waiteraid`.

`POST /wa-api/searchBooking` returns an envelope `{"status": "OK", "bookings": [...]}`.
The connector must emit one record per element of `bookings`, not the envelope itself.
"""

import json
from typing import Any, Dict
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"auth_hash": "test-hash", "restid": "1234", "start_date": "2026-09-01"}


def _booking(booking_id: int, date: str) -> Dict[str, Any]:
    return {"id": booking_id, "date": date, "amount": 2, "guest": {"id": booking_id * 10, "firstname": "Ada"}}


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking_in_envelope(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            HttpRequest(
                url="https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"date": "2026-09-01", "auth_hash": "test-hash", "restid": "1234"},
            ),
            HttpResponse(
                body=json.dumps({"status": "OK", "bookings": [_booking(9001, "2026-09-03"), _booking(9002, "2026-09-04")]}),
                status_code=200,
            ),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        records = [r.record.data for r in output.records]
        assert [r.get("id") for r in records] == [9001, 9002]
        assert [r["date"] for r in records] == ["2026-09-03", "2026-09-04"]
        assert [r["guest"]["id"] for r in records] == [90010, 90020]
        assert all("bookings" not in r for r in records)
