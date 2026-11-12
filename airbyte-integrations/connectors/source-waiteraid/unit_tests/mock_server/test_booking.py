# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    "bookings",
    [
        [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
            {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
        ],
        [],
    ],
    ids=["two_bookings", "empty_bookings"],
)
def test_read_emits_individual_bookings(bookings):
    config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "42"}
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))
        output = read(get_source(config), config=config, catalog=catalog)
        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert len(records) == len(bookings)
    assert [record["id"] for record in records] == [record["id"] for record in bookings]
    assert records == bookings
    assert all("status" not in record and "bookings" not in record for record in records)
