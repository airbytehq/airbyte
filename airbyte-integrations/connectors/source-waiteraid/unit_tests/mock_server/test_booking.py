# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_STREAM_NAME = "booking"
_SEARCH_BOOKING_URL = "https://app.waiteraid.com/wa-api/searchBooking"


def _search_booking_request(config: dict) -> HttpRequest:
    return HttpRequest(
        url=_SEARCH_BOOKING_URL,
        query_params={
            "date": config["start_date"],
            "auth_hash": config["auth_hash"],
            "restid": config["restid"],
        },
    )


def _read_booking(config: dict):
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog)


class TestBookingStream(TestCase):
    @HttpMocker()
    def test_read_emits_one_record_per_booking_from_bookings_envelope(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().build()
        http_mocker.post(
            _search_booking_request(config),
            HttpResponse(
                body=json.dumps(
                    {
                        "status": "OK",
                        "bookings": [
                            {
                                "id": 9001,
                                "date": "2026-09-03",
                                "amount": 2,
                                "status": "confirmed",
                                "guest": {"id": 11, "firstname": "Ada", "lastname": "Lovelace"},
                            },
                            {
                                "id": 9002,
                                "date": "2026-09-04",
                                "amount": 4,
                                "status": "cancelled",
                                "guest": {"id": 12, "firstname": "Alan", "lastname": "Turing"},
                            },
                        ],
                    }
                ),
                status_code=200,
            ),
        )

        output = _read_booking(config)

        records = [record.record.data for record in output.records]
        assert [record.get("id") for record in records] == [9001, 9002]
        assert [record["date"] for record in records] == ["2026-09-03", "2026-09-04"]
        assert [record["amount"] for record in records] == [2, 4]
        assert [record["status"] for record in records] == ["confirmed", "cancelled"]
        assert [record["guest"]["id"] for record in records] == [11, 12]
        assert all("bookings" not in record for record in records)

    @HttpMocker()
    def test_read_emits_no_records_when_bookings_is_empty(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().build()
        http_mocker.post(
            _search_booking_request(config),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": []}), status_code=200),
        )

        output = _read_booking(config)

        assert output.records == []
