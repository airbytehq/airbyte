# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import requests
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "1", "guest": {"id": 101, "firstname": "Test"}},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "2", "guest": {"id": 102, "firstname": "Example"}},
]


@pytest.mark.parametrize("stream_location", ["definitions", "streams"])
@pytest.mark.parametrize(
    "payload, expected",
    [
        pytest.param({"status": "OK", "bookings": BOOKINGS}, BOOKINGS, id="multiple-bookings"),
        pytest.param({"status": "OK", "bookings": BOOKINGS[:1]}, BOOKINGS[:1], id="single-booking"),
        pytest.param({"status": "OK", "bookings": []}, [], id="empty-bookings"),
        pytest.param({"status": "OK"}, [], id="missing-bookings"),
    ],
)
def test_booking_extractor(stream_location: str, payload: dict, expected: list[dict]) -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    stream = manifest["definitions"]["streams"]["booking"] if stream_location == "definitions" else manifest["streams"][0]
    extractor = DpathExtractor(
        field_path=stream["retriever"]["record_selector"]["extractor"]["field_path"],
        config=CONFIG,
        parameters={},
    )
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode()

    assert list(extractor.extract_records(response)) == expected


@pytest.mark.parametrize("bookings", [BOOKINGS, []], ids=["populated", "empty"])
def test_booking_stream_reads_individual_bookings(bookings: list[dict]) -> None:
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=CONFIG, catalog=catalog)
    with requests_mock.Mocker() as http_mock:
        http_mock.post(
            "https://app.waiteraid.com/wa-api/searchBooking",
            json={"status": "OK", "bookings": bookings},
        )
        output = read(source, config=CONFIG, catalog=catalog)

    assert output.errors == [], output.get_formatted_error_message()
    assert [record.record.data for record in output.records] == bookings
    assert http_mock.call_count == 1
    assert http_mock.last_request.qs == {key: [value] for key, value in CONFIG.items() if key != "start_date"} | {
        "date": [CONFIG["start_date"]]
    }
