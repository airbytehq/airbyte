# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}


def _request() -> HttpRequest:
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


def _read():
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), config=CONFIG, catalog=catalog)


def test_read_emits_each_booking(http_mocker: HttpMocker):
    bookings = [
        {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
        {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
    ]
    request = _request()
    http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))

    output = _read()

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert [record.get("id") for record in records] == [9001, 9002]
    assert records == bookings
    http_mocker.assert_number_of_calls(request, 1)


def test_read_empty_bookings_emits_no_records(http_mocker: HttpMocker):
    request = _request()
    http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": []}), status_code=200))

    output = _read()

    assert output.errors == []
    assert output.records == []
    http_mocker.assert_number_of_calls(request, 1)
