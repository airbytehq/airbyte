# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_read_emits_one_record_per_booking(http_mocker: HttpMocker) -> None:
    config = {"start_date": "2026-09-03", "auth_hash": "fake-auth-hash", "restid": "fake-restaurant"}
    bookings = [
        {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1001}},
        {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 1002}},
        {"id": 9003, "date": "2026-09-03", "amount": 1, "guest": {"id": 1003}},
    ]
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )
    http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog)

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert [record.get("id") for record in records] == [9001, 9002, 9003]
    assert [record["date"] for record in records] == ["2026-09-03"] * 3
    assert [record["amount"] for record in records] == [2, 4, 1]
    http_mocker.assert_number_of_calls(request, 1)
