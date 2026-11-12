# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


@pytest.mark.parametrize("bookings", [[{"id": 9001, "amount": 2}, {"id": 9002, "amount": 4}], []])
def test_read_emits_individual_bookings(bookings):
    config = {"start_date": "2026-11-11", "auth_hash": "test-auth-hash", "restid": "123"}
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
    assert len(output.records) == len(bookings)
    assert [message.record.data["id"] for message in output.records] == [booking["id"] for booking in bookings]
