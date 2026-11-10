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
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Alice"}},
            {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "name": "Bob"}},
        ],
        [],
    ],
    ids=["multiple-bookings", "empty-bookings"],
)
def test_read_emits_bookings_not_response_envelope(bookings):
    config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            request,
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )
        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build(),
        )
        http_mocker.assert_number_of_calls(request, 1)

    records = [message.record.data for message in output.records]
    assert [record.get("id") for record in records] == [booking["id"] for booking in bookings]
    assert records == bookings
    assert not output.errors


def test_read_does_not_emit_http_error_response():
    config = {"start_date": "2026-09-03", "auth_hash": "invalid-auth-hash", "restid": "123"}
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-03", "auth_hash": "invalid-auth-hash", "restid": "123"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            request,
            HttpResponse(body=json.dumps({"status": "ERROR", "message": "Unauthorized"}), status_code=401),
        )
        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build(),
            expecting_exception=True,
        )
        http_mocker.assert_number_of_calls(request, 1)

    assert output.records == []
    assert output.errors
    assert any(error.trace.error.failure_type.value == "config_error" for error in output.errors)
