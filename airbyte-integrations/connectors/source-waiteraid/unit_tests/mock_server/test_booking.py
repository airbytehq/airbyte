# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"start_date": "2024-01-01", "auth_hash": "test-auth-hash", "restid": "123"}
BOOKINGS = [
    {"id": 101, "date": "2024-01-02", "amount": 2, "guest": {"id": 11, "name": "Test Guest One"}},
    {"id": 102, "date": "2024-01-03", "amount": 4, "guest": {"id": 12, "name": "Test Guest Two"}},
    {"id": 103, "date": "2024-01-04", "amount": 1, "guest": {"id": 13, "name": "Test Guest Three"}},
]


def booking_request() -> HttpRequest:
    return HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": CONFIG["start_date"], "auth_hash": CONFIG["auth_hash"], "restid": CONFIG["restid"]},
    )


def read_booking(expecting_exception=False):
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    manifest = Path(__file__).parents[2] / "manifest.yaml"
    if not manifest.exists():
        manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    source = YamlDeclarativeSource(path_to_yaml=str(manifest), config=CONFIG, catalog=catalog, state=[])
    return read(source, config=CONFIG, catalog=catalog, expecting_exception=expecting_exception)


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["multiple_bookings", "empty_bookings"])
def test_booking_records(http_mocker: HttpMocker, bookings):
    request = booking_request()
    http_mocker.post(request, HttpResponse(json.dumps({"status": "OK", "bookings": bookings})))

    output = read_booking()

    assert not output.errors
    records = [message.record.data for message in output.records]
    assert [record.get("id") for record in records] == [booking["id"] for booking in bookings]
    assert all("status" not in record and "bookings" not in record for record in records)
    assert records == bookings
    http_mocker.assert_number_of_calls(request, 1)


def test_booking_http_error(http_mocker: HttpMocker):
    request = booking_request()
    http_mocker.post(request, HttpResponse(json.dumps({"status": "Unauthorized"}), status_code=401))

    output = read_booking(expecting_exception=True)

    assert output.errors
    assert not output.records
    http_mocker.assert_number_of_calls(request, 1)
