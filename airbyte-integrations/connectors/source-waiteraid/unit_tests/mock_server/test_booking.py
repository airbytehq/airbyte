# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import WaiteraidRequestBuilder


_STREAM_NAME = "booking"


def _booking(booking_id: int, date: str) -> Dict[str, Any]:
    return {
        "id": booking_id,
        "date": date,
        "amount": 2,
        "status": "confirmed",
        "guest": {"id": booking_id * 10, "firstname": "Ada", "lastname": "Lovelace"},
    }


def _search_booking_response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


class TestBooking(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking_in_the_response_envelope(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_auth_hash("hash-abc").with_restid("1234").with_start_date("2026-09-01").build()
        bookings = [_booking(9001, "2026-09-03"), _booking(9002, "2026-09-04")]
        http_mocker.post(
            WaiteraidRequestBuilder.search_booking_endpoint(auth_hash="hash-abc", restid="1234", date="2026-09-01").build(),
            _search_booking_response(bookings),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

        assert [record.record.data for record in output.records] == bookings
