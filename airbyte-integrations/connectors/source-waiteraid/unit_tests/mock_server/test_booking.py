# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"auth_hash": "test-hash", "restid": "1234", "start_date": "2026-09-01"}


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test-hash", "restid": "1234"},
    )


def _search_booking_response(bookings: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200)


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_emits_one_record_per_booking_in_response(self, http_mocker: HttpMocker) -> None:
        bookings = [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1, "name": "Ada"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 2, "name": "Grace"}},
        ]
        http_mocker.post(_search_booking_request(), _search_booking_response(bookings))

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert [record.record.data for record in output.records] == bookings
