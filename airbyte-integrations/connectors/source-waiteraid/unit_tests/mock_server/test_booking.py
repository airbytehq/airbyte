# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source
from jsonschema import validate

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "x", "restid": "1234", "start_date": "2026-09-01"}
REQUEST = HttpRequest(
    url="https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-09-01", "auth_hash": "x", "restid": "1234"},
)
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
]


def read_booking(expect_error=False):
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expect_error)


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["two-bookings", "empty"])
def test_booking_records(bookings):
    with HttpMocker() as http_mocker:
        http_mocker.post(REQUEST, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings})))
        output = read_booking()
        http_mocker.assert_number_of_calls(REQUEST, 1)

    records = [record.record.data for record in output.records]
    assert len(records) == len(bookings)
    assert [record["id"] for record in records] == [booking["id"] for booking in bookings]
    assert records == bookings
    assert not output.errors
    schema = get_source(CONFIG).streams(CONFIG)[0].get_json_schema()
    for record in records:
        validate(record, schema)


def test_booking_authentication_error():
    with HttpMocker() as http_mocker:
        http_mocker.post(REQUEST, HttpResponse(body=json.dumps({"status": "Unauthorized"}), status_code=401))
        output = read_booking(expect_error=True)
        http_mocker.assert_number_of_calls(REQUEST, 1)

    assert not output.records
    assert output.errors
