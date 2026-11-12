# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-auth-hash", "restid": "123", "start_date": "2026-11-01"}
BOOKINGS = [
    {"id": 9001, "date": "2026-11-01", "amount": 2},
    {"id": 9002, "date": "2026-11-02", "amount": 4},
]


def read_bookings(http_mocker, response):
    http_mocker.post(
        HttpRequest(
            url="https://app.waiteraid.com/wa-api/searchBooking",
            query_params={
                "auth_hash": CONFIG["auth_hash"],
                "restid": CONFIG["restid"],
                "date": CONFIG["start_date"],
            },
        ),
        HttpResponse(body=json.dumps(response), status_code=200),
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), config=CONFIG, catalog=catalog)


def test_full_refresh_emits_individual_bookings():
    with HttpMocker() as http_mocker:
        output = read_bookings(http_mocker, {"status": "OK", "bookings": BOOKINGS})

    assert len(output.records) == 2
    records = {message.record.data["id"]: message.record.data for message in output.records}
    assert set(records) == {9001, 9002}
    for booking in BOOKINGS:
        assert records[booking["id"]]["date"] == booking["date"]
        assert records[booking["id"]]["amount"] == booking["amount"]


@pytest.mark.parametrize("response", [{"status": "OK", "bookings": []}, {"status": "OK"}], ids=["empty", "missing"])
def test_no_bookings_emits_no_records(response):
    with HttpMocker() as http_mocker:
        output = read_bookings(http_mocker, response)

    assert len(output.records) == 0
    assert not any(log.log.level == "ERROR" for log in output.logs)
