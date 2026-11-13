# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import read_stream
from jsonschema import Draft7Validator

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("empty", [False, True])
def test_single_full_schedule_request(http_mocker: HttpMocker, empty: bool) -> None:
    request = HttpRequest("https://api.tvmaze.com/schedule/full", query_params={})
    records = [] if empty else [{"id": 3, "airdate": "2024-02-01", "name": "Future episode"}]
    http_mocker.get(request, HttpResponse(json.dumps(records)))

    output = read_stream("future", SyncMode.full_refresh)

    assert output.errors == []
    assert [record.record.data for record in output.records] == records
    http_mocker.assert_number_of_calls(request, 1)


def test_records_match_discovered_schema(http_mocker: HttpMocker, discovered_schemas: dict[str, dict]) -> None:
    record = {
        "id": 3,
        "name": "Future episode",
        "airdate": "2024-02-01",
        "image": {"medium": "https://example.com/episode.jpg", "original": "https://example.com/episode-original.jpg"},
        "rating": {"average": None},
        "show": {
            "id": 30,
            "name": "Future show",
            "dvdCountry": None,
            "externals": {"tvrage": None},
            "network": {"officialSite": "https://example.com"},
            "officialSite": "https://example.com",
            "rating": {"average": 8.5},
            "webChannel": None,
        },
    }
    request = HttpRequest("https://api.tvmaze.com/schedule/full", query_params={})
    http_mocker.get(request, HttpResponse(json.dumps([record])))

    output = read_stream("future", SyncMode.full_refresh)

    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]
    schema = discovered_schemas["future"]
    for message in output.records:
        assert list(Draft7Validator(schema).iter_errors(message.record.data)) == []
    Draft7Validator.check_schema(schema)
    http_mocker.assert_number_of_calls(request, 1)
