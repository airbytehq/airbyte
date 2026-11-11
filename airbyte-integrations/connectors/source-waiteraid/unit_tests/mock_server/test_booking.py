# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "12345"}


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def _read_bookings(http_mocker: HttpMocker, bookings: list):
    http_mocker.post(
        HttpRequest(
            url="https://app.waiteraid.com/wa-api/searchBooking",
            query_params={"date": _CONFIG["start_date"], "auth_hash": _CONFIG["auth_hash"], "restid": _CONFIG["restid"]},
        ),
        HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)


def test_read_emits_one_record_per_booking(http_mocker: HttpMocker) -> None:
    bookings = [
        {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Alice"}},
        {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "name": "Bob"}},
    ]

    output = _read_bookings(http_mocker, bookings)

    assert not output.errors
    assert len(output.records) == 2
    records = [message.record.data for message in output.records]
    assert {record["id"] for record in records} == {9001, 9002}
    assert {record["id"]: (record["date"], record["amount"]) for record in records} == {
        9001: ("2026-09-03", 2),
        9002: ("2026-09-04", 4),
    }
    assert all("status" not in record and "bookings" not in record for record in records)
    assert all(message.record.stream == "booking" for message in output.records)


def test_read_empty_bookings_emits_no_records(http_mocker: HttpMocker) -> None:
    output = _read_bookings(http_mocker, [])

    assert not output.errors
    assert len(output.records) == 0
