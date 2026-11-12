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


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_full_refresh_emits_one_record_per_booking(self, http_mocker: HttpMocker) -> None:
        """searchBooking wraps bookings in {"status", "bookings"}; each booking must be its own record."""
        http_mocker.post(
            _search_booking_request(),
            HttpResponse(
                body=json.dumps(
                    {
                        "status": "OK",
                        "bookings": [
                            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1, "name": "Ada"}},
                            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 2, "name": "Grace"}},
                        ],
                    }
                ),
                status_code=200,
            ),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert [record.record.data for record in output.records] == [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1, "name": "Ada"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 2, "name": "Grace"}},
        ]
