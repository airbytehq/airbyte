# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import re
from collections import Counter
from datetime import date, timedelta

import pytest
from conftest import base_config, get_source
from freezegun import freeze_time
from test_campaign_report import _FIELDS, _REPORT_URL, _mock_token, _read_report_windows

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_PLACEHOLDER_ID = "a2_abc123"
_AD_ACCOUNT_URL = f"https://ads-api.reddit.com/api/v3/ad_accounts/{_PLACEHOLDER_ID}"
_AD_GROUP_URL = f"{_AD_ACCOUNT_URL}/ad_groups"
_REPORT_CASES = [
    ("ad_account_report", ["AD_ACCOUNT_ID", "DATE"], ["account_id", "date"], []),
    ("ad_group_report", ["AD_GROUP_ID", "DATE"], ["ad_group_id", "date"], ["CAMPAIGN_ID"]),
    ("ad_report", ["AD_ID", "DATE"], ["ad_id", "date"], ["CAMPAIGN_ID"]),
]


def _report_record(report_date: str) -> dict:
    return {
        "account_id": _PLACEHOLDER_ID,
        "ad_group_id": _PLACEHOLDER_ID,
        "ad_id": _PLACEHOLDER_ID,
        "campaign_id": _PLACEHOLDER_ID,
        "date": report_date,
    }


def _normalize_report_body(body: dict) -> dict:
    data = body["data"]
    return {
        "data": {
            **data,
            "fields": sorted(data["fields"]),
            "breakdowns": sorted(data["breakdowns"]),
        }
    }


def _expected_report_body(breakdowns: list[str], extra_fields: list[str]) -> dict:
    return {
        "data": {
            "starts_at": "2026-10-14T00:00:00Z",
            "ends_at": "2026-10-15T09:00:00Z",
            "fields": [*_FIELDS, *extra_fields],
            "breakdowns": breakdowns,
            "time_zone_id": "GMT",
        }
    }


def _catalog(stream_name: str, sync_mode: SyncMode = SyncMode.incremental):
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def test_ad_account_reads_one_record_with_id() -> None:
    config = base_config()
    catalog = _catalog("ad_account", SyncMode.full_refresh)
    request = HttpRequest(_AD_ACCOUNT_URL)

    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"data": {"id": _PLACEHOLDER_ID}}), status_code=200),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data["id"] == _PLACEHOLDER_ID
    http_mocker.assert_number_of_calls(request, 1)


def test_ad_group_paginates_and_filters_modified_at_client_side() -> None:
    config = base_config(start_time="2026-09-26T00:00:00Z")
    catalog = _catalog("ad_group")
    first_request = HttpRequest(_AD_GROUP_URL)
    next_request = HttpRequest(_AD_GROUP_URL, query_params={"page.token": "cursor="})
    first_page = {
        "data": [
            {"id": "a2_abc123", "name": "before-start", "modified_at": "2026-09-25T00:00:00Z"},
            {"id": "a2_def456", "name": "kept-first", "modified_at": "2026-09-27T00:00:00Z"},
        ],
        "pagination": {"next_url": f"{_AD_GROUP_URL}?page.token=cursor%3D"},
    }
    second_page = {"data": [{"id": "a2_ghi789", "name": "kept-second", "modified_at": "2026-09-28T00:00:00Z"}]}

    with freeze_time("2026-10-17T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(first_request, HttpResponse(body=json.dumps(first_page), status_code=200))
        http_mocker.get(next_request, HttpResponse(body=json.dumps(second_page), status_code=200))
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert {message.record.data["name"] for message in output.records} == {"kept-first", "kept-second"}
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(next_request, 1)


@pytest.mark.parametrize("stream_name,breakdowns,primary_key,extra_fields", _REPORT_CASES)
def test_report_request_body_and_primary_key_fields(
    stream_name: str,
    breakdowns: list[str],
    primary_key: list[str],
    extra_fields: list[str],
) -> None:
    config = base_config(start_time="2026-10-14T00:00:00Z")
    catalog = _catalog(stream_name)
    expected = _expected_report_body(breakdowns, extra_fields)

    with freeze_time("2026-10-15T09:30:00Z"), HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _REPORT_URL,
            text=lambda _request, _context: json.dumps({"data": {"metrics": [_report_record("2026-10-14")]}}),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)
        sent_bodies = [request.json() for request in http_mocker._mocker.request_history if request.url == _REPORT_URL]

    assert output.errors == []
    assert len(sent_bodies) == 1
    assert _normalize_report_body(sent_bodies[0]) == _normalize_report_body(expected)
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record[primary_key[0]] == _PLACEHOLDER_ID
    assert record["date"] == "2026-10-14"


@pytest.mark.parametrize("stream_name,breakdowns,primary_key,extra_fields", _REPORT_CASES)
def test_report_windows_tile_and_emit_each_date_once(
    stream_name: str,
    breakdowns: list[str],
    primary_key: list[str],
    extra_fields: list[str],
) -> None:
    config = base_config(start_time="2026-10-02T05:00:00Z")
    windows, emitted_dates = _read_report_windows(
        "2026-10-14T16:30:00Z",
        config,
        stream_name=stream_name,
    )
    expected_windows = [
        ("2026-10-02T00:00:00Z", "2026-10-05T00:00:00Z"),
        ("2026-10-05T00:00:00Z", "2026-10-08T00:00:00Z"),
        ("2026-10-08T00:00:00Z", "2026-10-11T00:00:00Z"),
        ("2026-10-11T00:00:00Z", "2026-10-14T00:00:00Z"),
        ("2026-10-14T00:00:00Z", "2026-10-14T16:00:00Z"),
    ]
    expected_dates = Counter((date(2026, 10, 2) + timedelta(days=offset)).isoformat() for offset in range(13))

    assert sorted(windows) == sorted(expected_windows)
    assert windows[0][0] == "2026-10-02T00:00:00Z"
    assert windows[-1][1] == "2026-10-14T16:00:00Z"
    assert all(windows[index][1] == windows[index + 1][0] for index in range(len(windows) - 1))
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:00:00Z", boundary) for window in windows for boundary in window)
    assert Counter(emitted_dates) == expected_dates


@pytest.mark.parametrize("stream_name,breakdowns,primary_key,extra_fields", _REPORT_CASES)
def test_report_retries_5xx_with_shared_handler(
    stream_name: str,
    breakdowns: list[str],
    primary_key: list[str],
    extra_fields: list[str],
    monkeypatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    config = base_config(start_time="2026-10-14T00:00:00Z")
    catalog = _catalog(stream_name)
    expected = _expected_report_body(breakdowns, extra_fields)

    with freeze_time("2026-10-15T09:30:00Z"), HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _REPORT_URL,
            [
                {"status_code": 503, "text": '{"error":{"message":"Service Unavailable"}}'},
                {
                    "status_code": 200,
                    "text": json.dumps({"data": {"metrics": [_report_record("2026-10-14")]}}),
                },
            ],
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)
        sent_bodies = [item.json() for item in http_mocker._mocker.request_history if item.url == _REPORT_URL]

    assert output.errors == []
    assert len(sent_bodies) == 2
    assert all(_normalize_report_body(body) == _normalize_report_body(expected) for body in sent_bodies)
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record[primary_key[0]] == _PLACEHOLDER_ID
    assert record["date"] == "2026-10-14"
