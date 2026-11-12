# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    "bookings",
    [
        [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Test Guest"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "name": "Another Guest"}},
        ],
        [],
    ],
    ids=["populated-bookings", "empty-bookings"],
)
def test_read_emits_individual_bookings(bookings: list[dict]) -> None:
    config = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    local_manifest = Path(__file__).resolve().parents[2] / "manifest.yaml"
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    source = YamlDeclarativeSource(
        path_to_yaml=str(ci_manifest if ci_manifest.exists() else local_manifest),
        config=config,
        catalog=catalog,
        state=[],
    )
    request = HttpRequest(
        url="https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))
        output = read(source, config=config, catalog=catalog)
        http_mocker.assert_number_of_calls(request, 1)

    actual_records = [message.record.data for message in output.records]
    assert len(actual_records) == len(bookings)
    assert sorted(actual_records, key=lambda record: record["id"]) == bookings
