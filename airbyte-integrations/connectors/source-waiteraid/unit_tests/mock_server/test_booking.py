# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_booking_emits_individual_bookings(source, config):
    bookings = [
        {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
        {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
    ]
    request = HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(json.dumps({"status": "OK", "bookings": bookings})))
        output = read(source, config=config, catalog=catalog)
        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert len(records) == 2
    assert [record["id"] for record in records] == [9001, 9002]
    assert records == bookings
