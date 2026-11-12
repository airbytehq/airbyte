# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "First Guest"}},
    {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "name": "Second Guest"}},
]


def booking_request():
    return HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


def read_booking():
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), config=CONFIG, catalog=catalog)


def test_booking_emits_individual_records():
    request = booking_request()
    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": BOOKINGS}), status_code=200))
        output = read_booking()
        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 2
    records = [message.record.data for message in output.records]
    assert [record["id"] for record in records] == [9001, 9002]
    assert [record["date"] for record in records] == ["2026-09-03", "2026-09-03"]
    assert [record["amount"] for record in records] == [2, 4]


@pytest.mark.parametrize("body", [{"status": "OK", "bookings": []}, {"status": "OK"}])
def test_booking_empty_response_emits_no_records(body):
    with HttpMocker() as http_mocker:
        http_mocker.post(booking_request(), HttpResponse(body=json.dumps(body), status_code=200))
        output = read_booking()

    assert output.errors == []
    assert output.records == []


def test_booking_http_error_emits_no_records():
    with HttpMocker() as http_mocker:
        http_mocker.post(booking_request(), HttpResponse(body=json.dumps({"status": "Unauthorized"}), status_code=401))
        output = read_booking()

    assert output.errors
    assert output.records == []
