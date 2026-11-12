# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-auth-hash", "restid": "123", "start_date": "2026-11-01"}
REQUEST = HttpRequest(
    "https://app.waiteraid.com/wa-api/searchBooking",
    query_params={"date": "2026-11-01", "auth_hash": "test-auth-hash", "restid": "123"},
)


def read_booking() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )
    return read(source, config=CONFIG, catalog=catalog, state=[])


def test_booking_records(http_mocker: HttpMocker) -> None:
    bookings = [
        {"id": 101, "guest": {"id": 201, "name": "Ada Lovelace"}},
        {"id": 102, "guest": {"id": 202, "name": "Grace Hopper"}},
        {"id": 103, "guest": {"id": 203, "name": "Katherine Johnson"}},
    ]
    http_mocker.post(REQUEST, HttpResponse(json.dumps({"status": "OK", "bookings": bookings})))

    output = read_booking()

    assert len(output.records) == 3
    records = [record.record.data for record in output.records]
    assert [record["id"] for record in records] == [101, 102, 103]
    assert [record["guest"] for record in records] == [booking["guest"] for booking in bookings]
    assert output.errors == []
    http_mocker.assert_number_of_calls(REQUEST, 1)


def test_empty_bookings(http_mocker: HttpMocker) -> None:
    http_mocker.post(REQUEST, HttpResponse(json.dumps({"status": "OK", "bookings": []})))

    output = read_booking()

    assert len(output.records) == 0
    assert output.errors == []
    assert not any(message.log.level == Level.ERROR for message in output.logs)
    http_mocker.assert_number_of_calls(REQUEST, 1)
