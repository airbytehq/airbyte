# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import base_config, get_source
from freezegun import freeze_time
from test_campaign_report import _FIELDS, _REPORT_URL, _days, _mock_token, _report_record, _sync

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_PLACEHOLDER_ID = "a2_abc123"
_REPORT_STREAMS = [
    ("campaign_report", ["campaign_id", "date"], {"campaign_id": _PLACEHOLDER_ID}),
    ("ad_account_report", ["AD_ACCOUNT_ID", "DATE"], {"account_id": base_config()["ad_account_id"]}),
    ("ad_group_report", ["AD_GROUP_ID", "CAMPAIGN_ID", "DATE"], {"ad_group_id": _PLACEHOLDER_ID, "campaign_id": _PLACEHOLDER_ID}),
    ("ad_report", ["AD_ID", "CAMPAIGN_ID", "DATE"], {"ad_id": _PLACEHOLDER_ID, "campaign_id": _PLACEHOLDER_ID}),
]
_REPORT_STREAM_NAMES = [stream_name for stream_name, *_ in _REPORT_STREAMS]
_INITIAL_WINDOWS = [
    ("2026-10-02T00:00:00Z", "2026-10-05T00:00:00Z"),
    ("2026-10-05T00:00:00Z", "2026-10-08T00:00:00Z"),
    ("2026-10-08T00:00:00Z", "2026-10-11T00:00:00Z"),
    ("2026-10-11T00:00:00Z", "2026-10-14T00:00:00Z"),
    ("2026-10-14T00:00:00Z", "2026-10-14T16:00:00Z"),
]


def _catalog(stream_name: str):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _report_body(breakdowns: list[str], start: str, end: str) -> dict:
    return {
        "data": {
            "starts_at": start,
            "ends_at": end,
            "fields": _FIELDS,
            "breakdowns": breakdowns,
            "time_zone_id": "GMT",
        }
    }


@pytest.mark.parametrize("stream_name", _REPORT_STREAM_NAMES)
def test_empty_report_response_keeps_contiguous_windows_and_final_state(
    stream_name: str,
) -> None:
    config = base_config(start_time="2026-10-02T05:00:00Z")
    catalog = _catalog(stream_name)

    with freeze_time("2026-10-14T16:30:00Z"), HttpMocker() as http_mocker:
        http_mocker._mocker.post(_REPORT_URL, json={"data": {"metrics": []}, "pagination": {}})
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)
        report_requests = [request for request in http_mocker._mocker.request_history if request.url == _REPORT_URL]
        windows = sorted((request.json()["data"]["starts_at"], request.json()["data"]["ends_at"]) for request in report_requests)

    assert output.errors == []
    assert output.records == []
    assert len(report_requests) == len(_INITIAL_WINDOWS)
    assert windows == _INITIAL_WINDOWS
    assert all(windows[index][1] == windows[index + 1][0] for index in range(len(windows) - 1))
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-10-02"


@pytest.mark.parametrize("stream_name,breakdowns,expected_ids", _REPORT_STREAMS)
def test_report_retries_429_for_one_window(
    stream_name: str,
    breakdowns: list[str],
    expected_ids: dict,
    monkeypatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    config = base_config(start_time="2026-10-14T00:00:00Z")
    catalog = _catalog(stream_name)
    expected_window = ("2026-10-14T00:00:00Z", "2026-10-15T09:00:00Z")

    with freeze_time("2026-10-15T09:30:00Z"), HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _REPORT_URL,
            [
                {
                    "status_code": 429,
                    "text": '{"error":{"message":"Rate limited"}}',
                    "headers": {"ratelimit-remaining": "399"},
                },
                {
                    "status_code": 200,
                    "text": json.dumps(
                        {"data": {"metrics": [_report_record(breakdowns, "2026-10-14", _PLACEHOLDER_ID)]}, "pagination": {}}
                    ),
                },
            ],
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)
        report_requests = [request for request in http_mocker._mocker.request_history if request.url.split("?")[0] == _REPORT_URL]
        windows = [(request.json()["data"]["starts_at"], request.json()["data"]["ends_at"]) for request in report_requests]

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data.items() >= expected_ids.items()
    assert output.records[0].record.data["date"] == "2026-10-14"
    assert windows == [expected_window, expected_window]
    window_count = len(set(windows))
    assert len(report_requests) == window_count + 1


@pytest.mark.parametrize("stream_name", _REPORT_STREAM_NAMES)
@pytest.mark.parametrize("inclusive_end", [False, True], ids=["exclusive_ends_at", "inclusive_ends_at"])
def test_report_second_sync_from_emitted_state_rereads_whole_days(
    stream_name: str,
    inclusive_end: bool,
) -> None:
    config = base_config(start_time="2026-10-02T00:00:00Z")
    _, _, state = _sync("2026-10-14T16:30:00Z", config, inclusive_end, stream_name=stream_name)
    _, table, _ = _sync("2026-10-15T09:30:00Z", config, inclusive_end, state=[state], stream_name=stream_name)

    assert state.stream.stream_state.date == "2026-10-14"
    assert table == {**_days(7, 14), "2026-10-15": 9 + inclusive_end}


@pytest.mark.parametrize("stream_name,breakdowns,_expected_ids", _REPORT_STREAMS)
def test_report_paginates_and_decodes_percent_encoded_token(
    stream_name: str,
    breakdowns: list[str],
    _expected_ids: dict,
) -> None:
    config = base_config(start_time="2026-10-14T00:00:00Z")
    catalog = _catalog(stream_name)
    request_body = _report_body(
        breakdowns,
        "2026-10-14T00:00:00Z",
        "2026-10-15T09:00:00Z",
    )
    first_identifier = "a2_abc123"
    second_identifier = "a2_def456"

    with freeze_time("2026-10-15T09:30:00Z"), HttpMocker() as http_mocker:
        first_request = HttpRequest(_REPORT_URL, body=request_body)
        next_page_request = HttpRequest(
            _REPORT_URL,
            query_params={"page.token": "cursor="},
            body=request_body,
        )
        http_mocker.post(
            first_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "data": {"metrics": [_report_record(breakdowns, "2026-10-14", first_identifier)]},
                        "pagination": {"next_url": f"{_REPORT_URL}?page.token=cursor%3D"},
                    }
                ),
                status_code=200,
            ),
        )
        http_mocker.post(
            next_page_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "data": {"metrics": [_report_record(breakdowns, "2026-10-14", second_identifier)]},
                        "pagination": {},
                    }
                ),
                status_code=200,
            ),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)
        report_requests = [request for request in http_mocker._mocker.request_history if request.url.split("?")[0] == _REPORT_URL]

    assert output.errors == []
    assert sorted(record.record.data[breakdowns[0].lower()] for record in output.records) == [first_identifier, second_identifier]
    assert len(report_requests) == 2
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(next_page_request, 1)


@pytest.mark.parametrize("stream_name,breakdowns,_expected_ids", _REPORT_STREAMS)
def test_report_legacy_timestamp_state_round_trips_to_plain_date(
    stream_name: str,
    breakdowns: list[str],
    _expected_ids: dict,
) -> None:
    config = base_config(start_time="2026-10-02T00:00:00Z", report_lookback_window_days=0)
    state = StateBuilder().with_stream_state(stream_name, {"date": "2026-10-13T00:00:00Z"}).build()
    rows = [_report_record(breakdowns, f"2026-10-{day}T00:00:00Z", _PLACEHOLDER_ID) for day in (13, 14)]

    with freeze_time("2026-10-15T00:30:00Z"), HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(_REPORT_URL, body=_report_body(breakdowns, "2026-10-13T00:00:00Z", "2026-10-15T00:00:00Z")),
            HttpResponse(body=json.dumps({"data": {"metrics": rows}}), status_code=200),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, _catalog(stream_name), state), config, _catalog(stream_name), state=state)

    assert output.errors == []
    assert [message.record.data["date"] for message in output.records] == ["2026-10-13", "2026-10-14"]
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-10-14"


@pytest.mark.parametrize("stream_name,breakdowns,_expected_ids", _REPORT_STREAMS)
def test_report_drops_null_date_rows_and_normalizes_the_rest(
    stream_name: str,
    breakdowns: list[str],
    _expected_ids: dict,
) -> None:
    config = base_config(start_time="2026-10-13T00:00:00Z", report_lookback_window_days=0)
    rows = [
        _report_record(breakdowns, None, _PLACEHOLDER_ID),
        _report_record(breakdowns, "2026-10-13T00:00:00Z", _PLACEHOLDER_ID),
        _report_record(breakdowns, "2026-10-14", _PLACEHOLDER_ID),
    ]

    with freeze_time("2026-10-15T00:30:00Z"), HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(_REPORT_URL, body=_report_body(breakdowns, "2026-10-13T00:00:00Z", "2026-10-15T00:00:00Z")),
            HttpResponse(body=json.dumps({"data": {"metrics": rows}}), status_code=200),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, _catalog(stream_name)), config, _catalog(stream_name))

    assert output.errors == []
    assert [message.record.data["date"] for message in output.records] == ["2026-10-13", "2026-10-14"]
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-10-14"
