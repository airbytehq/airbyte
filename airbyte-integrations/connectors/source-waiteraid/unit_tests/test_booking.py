# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"auth_hash": "h", "restid": "1234", "start_date": "2026-09-01"}
_REQUEST = HttpRequest(
    "https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-09-01", "auth_hash": "h", "restid": "1234"},
)


def _read(expecting_exception=False):
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


class TestBooking(TestCase):
    @HttpMocker()
    def test_emits_each_booking(self, http_mocker: HttpMocker):
        bookings = [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
        ]
        http_mocker.post(_REQUEST, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))

        output = _read()

        http_mocker.assert_number_of_calls(_REQUEST, 1)
        records = [record.record.data for record in output.records]
        assert len(records) == 2
        assert [record["id"] for record in records] == [9001, 9002]
        assert [(record["date"], record["amount"]) for record in records] == [("2026-09-03", 2), ("2026-09-04", 4)]
        assert records == bookings
        assert output.errors == []

    @HttpMocker()
    def test_empty_bookings(self, http_mocker: HttpMocker):
        http_mocker.post(_REQUEST, HttpResponse(body=json.dumps({"status": "OK", "bookings": []}), status_code=200))

        output = _read()

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_REQUEST, 1)

    @HttpMocker()
    def test_http_error_emits_no_bookings(self, http_mocker: HttpMocker):
        http_mocker.post(_REQUEST, HttpResponse(body=json.dumps({"status": "Unauthorized"}), status_code=401))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_REQUEST, 1)
