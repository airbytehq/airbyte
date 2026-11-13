# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-mrscraper` covering the manifest behaviours that are easy to regress:

- the API token is sent as both `x-api-token` and `Authorization: Bearer`, and a rejected token is a config error
- pagination follows `meta.page` and `meta.totalPage`, and stops when `meta` is missing
- every request sorts by `createdAt` ascending and filters `createdAt` by whole-day windows that neither
  overlap nor leave gaps
- incremental syncs resume one day before the saved state
- the credential-bearing `curl` field never reaches a record or the stream schema
"""

import json
import logging
from datetime import date, timedelta

import pytest
import requests_mock
from _helpers import (
    API_TOKEN,
    CONFIG,
    RESULTS_URL,
    days_ago,
    get_source,
    page,
    query_params,
    read_results,
    record_ids,
    result,
    today,
)

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


logger = logging.getLogger("airbyte")


def test_spec_marks_token_secret_and_start_date_optional():
    spec = get_source(CONFIG).spec(logger).connectionSpecification

    assert spec["required"] == ["api_key"]
    assert spec["properties"]["api_key"]["airbyte_secret"] is True
    assert spec["properties"]["start_date"]["format"] == "date"


def test_check_sends_token_in_both_headers():
    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, json=page([], total_page=0))
        status = get_source(CONFIG).check(logger, CONFIG)

    assert status.status == Status.SUCCEEDED
    request = mocker.request_history[0]
    assert request.headers["x-api-token"] == API_TOKEN
    assert request.headers["Authorization"] == f"Bearer {API_TOKEN}"


@pytest.mark.parametrize("status_code", [401, 403])
def test_rejected_token_is_config_error(status_code):
    body = {"message": "Unauthorized access", "errors": "Unauthorized"}
    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, status_code=status_code, json=body)
        status = get_source(CONFIG).check(logger, CONFIG)
        output = read_results({**CONFIG, "start_date": days_ago(1)})

    assert status.status == Status.FAILED
    assert "MrScraper rejected the API token" in status.message
    assert output.errors, "a rejected token must fail the read"
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error


def test_pagination_follows_meta_and_filters_by_day():
    start = days_ago(3)
    first = page([result("r-1", f"{start}T01:00:00.000Z"), result("r-2", f"{start}T02:00:00.000Z")], page_number=1, total_page=2)
    second = page([result("r-3", f"{days_ago(1)}T03:00:00.000Z")], page_number=2, total_page=2)

    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, [{"json": first}, {"json": second}])
        output = read_results({**CONFIG, "start_date": start})

    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert record_ids(output) == ["r-1", "r-2", "r-3"]
    assert len(mocker.request_history) == 2

    first_params, second_params = (query_params(request) for request in mocker.request_history)
    assert "page" not in first_params, "the first request must rely on MrScraper's default page 1"
    assert second_params["page"] == "2"
    for params in (first_params, second_params):
        assert params["pageSize"] == "50"
        assert params["sortField"] == "createdAt"
        assert params["sortOrder"] == "ASC"
        assert params["dateRangeColumn"] == "createdAt"
        assert params["startAt"] == start
        assert params["endAt"] == today().isoformat()


def test_pagination_stops_without_meta():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            RESULTS_URL,
            [
                {"json": {"message": "Successful fetch", "data": [result("r-1", f"{days_ago(1)}T00:00:00.000Z")]}},
                # A stop condition that is not null-safe would request another page; fail it loudly.
                {"status_code": 400, "json": {}},
            ],
        )
        output = read_results({**CONFIG, "start_date": days_ago(1)})

    assert record_ids(output) == ["r-1"]
    assert len(mocker.request_history) == 1


def test_default_start_date_covers_every_day_once():
    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, json=page([], total_page=0))
        output = read_results(CONFIG)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    windows = sorted(
        (date.fromisoformat(params["startAt"]), date.fromisoformat(params["endAt"])) for params in map(query_params, mocker.request_history)
    )
    assert windows[0][0] == date(2020, 1, 1)
    assert windows[-1][1] == today()
    for (_, previous_end), (next_start, _) in zip(windows, windows[1:]):
        assert next_start == previous_end + timedelta(days=1), "day windows must not overlap or leave gaps"
    assert all((end - start).days < 30 for start, end in windows)


def test_incremental_sync_resumes_one_day_before_state():
    state = StateBuilder().with_stream_state("results", {"createdAt": days_ago(2)}).build()
    records = [result("r-1", f"{days_ago(2)}T23:00:00.000Z"), result("r-2", f"{today().isoformat()}T08:00:00.000Z")]

    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, json=page(records))
        output = read_results(CONFIG, sync_mode=SyncMode.incremental, state=state)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert record_ids(output) == ["r-1", "r-2"]
    assert min(query_params(request)["startAt"] for request in mocker.request_history) == days_ago(3)
    assert output.most_recent_state.stream_state.__dict__["createdAt"] == today().isoformat()


def test_curl_field_is_never_synced():
    leaked = f"curl --location 'https://api.mrscraper.com/?url=https%3A%2F%2Fexample.com' -H 'x-api-token: {API_TOKEN}'"
    with requests_mock.Mocker() as mocker:
        mocker.get(RESULTS_URL, json=page([result("r-1", f"{days_ago(1)}T00:00:00.000Z", curl=leaked)]))
        output = read_results({**CONFIG, "start_date": days_ago(1)})

    records = [message.record.data for message in output.records]
    assert records, "expected one record"
    assert all("curl" not in record for record in records)
    assert API_TOKEN not in json.dumps(records)


def test_schema_declares_returned_fields_but_not_curl():
    properties = get_source(CONFIG).discover(logger, CONFIG).streams[0].json_schema["properties"]

    assert "curl" not in properties
    assert set(result("r-1", "2026-01-01T00:00:00.000Z")) <= set(properties)
