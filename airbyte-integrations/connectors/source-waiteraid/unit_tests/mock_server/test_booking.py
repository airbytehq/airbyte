# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import ExpectedOutcome, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-auth-hash", "restid": "123", "start_date": "2026-11-01"}


def booking_request():
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


def read_booking(expected_outcome=ExpectedOutcome.EXPECT_SUCCESS):
    return read(
        get_source(CONFIG),
        config=CONFIG,
        catalog=CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build(),
        expected_outcome=expected_outcome,
    )


class TestBooking(TestCase):
    @HttpMocker()
    def test_full_refresh_emits_each_booking(self, http_mocker):
        bookings = [
            {"id": 101, "date": "2026-11-01", "amount": 2, "guest": {"id": 11, "name": "Alice"}},
            {"id": 102, "date": "2026-11-01", "amount": 4, "guest": {"id": 12, "name": "Bob"}},
        ]
        http_mocker.post(booking_request(), HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings})))

        output = read_booking()

        assert len(output.records) == 2
        records = [message.record.data for message in output.records]
        assert [record["id"] for record in records] == [101, 102]
        assert records == bookings
        assert all("bookings" not in record for record in records)

    @HttpMocker()
    def test_empty_bookings_emits_no_records(self, http_mocker):
        http_mocker.post(booking_request(), HttpResponse(body=json.dumps({"status": "OK", "bookings": []})))

        output = read_booking()

        assert len(output.records) == 0
        assert not any(log.log.level == Level.ERROR for log in output.logs)

    @HttpMocker()
    def test_api_error_emits_no_records(self, http_mocker):
        http_mocker.post(booking_request(), HttpResponse(body=json.dumps({"error": "Invalid request"}), status_code=400))

        output = read_booking(expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        assert len(output.records) == 0
        assert any(log.log.level == Level.ERROR and "Invalid request" in log.log.message for log in output.logs)
