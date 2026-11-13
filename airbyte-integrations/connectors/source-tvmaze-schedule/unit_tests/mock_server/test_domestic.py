# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import read_stream
from jsonschema import Draft7Validator

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("mode", [SyncMode.full_refresh, SyncMode.incremental])
@pytest.mark.parametrize("empty", [False, True])
@pytest.mark.parametrize("end", ["", "2024-01-02"])
def test_daily_slices(http_mocker: HttpMocker, mode: SyncMode, empty: bool, end: str) -> None:
    records = []
    requests = []
    for day in (1, 2):
        date = f"2024-01-0{day}"
        request = HttpRequest("https://api.tvmaze.com/schedule", query_params={"date": date, "country": "GB"})
        batch = [] if empty else [{"id": day, "airdate": date, "name": f"Episode {day}"}]
        http_mocker.get(request, HttpResponse(json.dumps(batch)))
        requests.append(request)
        records.extend(batch)

    output = read_stream("domestic", mode, end=end)

    assert output.errors == []
    assert sorted((record.record.data for record in output.records), key=lambda record: record["id"]) == records
    if mode == SyncMode.incremental:
        assert output.most_recent_state.stream_state.airdate == ("2024-01-01" if empty else "2024-01-02")
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)


def test_resume(http_mocker: HttpMocker) -> None:
    request = HttpRequest("https://api.tvmaze.com/schedule", query_params={"date": "2024-01-02", "country": "GB"})
    records = [{"id": 2, "airdate": "2024-01-02", "name": "Episode 2"}]
    http_mocker.get(request, HttpResponse(json.dumps(records)))

    output = read_stream("domestic", cursor="2024-01-02")

    assert output.errors == []
    assert [record.record.data for record in output.records] == records
    assert output.most_recent_state.stream_state.airdate == "2024-01-02"
    http_mocker.assert_number_of_calls(request, 1)


def test_records_match_discovered_schema(http_mocker: HttpMocker, discovered_schemas: dict[str, dict]) -> None:
    record = {
        "id": 1,
        "name": "Domestic episode",
        "airdate": "2024-01-01",
        "show": {
            "id": 10,
            "name": "Domestic show",
            "dvdCountry": None,
            "network": {"officialSite": "https://example.com"},
            "webChannel": None,
        },
    }
    request = HttpRequest("https://api.tvmaze.com/schedule", query_params={"date": "2024-01-01", "country": "GB"})
    http_mocker.get(request, HttpResponse(json.dumps([record])))

    output = read_stream("domestic", SyncMode.full_refresh, end="2024-01-01")

    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]
    schema = discovered_schemas["domestic"]
    for message in output.records:
        assert list(Draft7Validator(schema).iter_errors(message.record.data)) == []
    Draft7Validator.check_schema(schema)
    http_mocker.assert_number_of_calls(request, 1)
