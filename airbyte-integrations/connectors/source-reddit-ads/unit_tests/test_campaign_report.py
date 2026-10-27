# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
import re
from collections import Counter
from datetime import datetime, timedelta

import pytest
from conftest import base_config, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_TOKEN_REQUEST_BODY = "grant_type=refresh_token&refresh_token=test-refresh-token"
_REPORT_URL = "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/reports"
_FIELDS = [
    "ACCOUNT_ID",
    "AD_CREATE_TIME",
    "AD_EFFECTIVE_STATUS",
    "AD_GROUP_ID",
    "AD_ID",
    "AD_UPDATE_TIME",
    "ADGROUP_CREATE_TIME",
    "ADGROUP_UPDATE_TIME",
    "IMPRESSIONS",
    "KEYWORD",
    "PLACEMENT",
    "POST_ID",
    "REACH",
    "REDDIT_LEADS",
    "REGION",
    "SPEND",
    "VIDEO_VIEWABLE_IMPRESSIONS",
    "ENGAGED_CLICK",
    "KEY_CONVERSION_CLICKS",
    "KEY_CONVERSION_ECPA",
    "KEY_CONVERSION_RATE",
    "KEY_CONVERSION_TOTAL_COUNT",
    "KEY_CONVERSION_VIEWS",
    "CPC",
    "COUNTRY",
    "CPV",
    "CTR",
    "FREQUENCY",
    "DATETIME",
    "ECPM",
    "CONVERSION_SIGN_UP_VIEWS",
    "CONVERSION_ROAS",
    "CONVERSION_SIGNUP_AVG_VALUE",
    "CONVERSION_SIGNUP_TOTAL_VALUE",
    "CONVERSION_VIEW_CONTENT_CLICKS",
    "CONVERSION_VIEW_CONTENT_ECPA",
    "CONVERSION_VIEW_CONTENT_VIEWS",
    "CONVERSION_LEAD_AVG_VALUE",
    "CONVERSION_LEAD_CLICKS",
    "CONVERSION_LEAD_ECPA",
    "CONVERSION_LEAD_TOTAL_VALUE",
    "CONVERSION_LEAD_VIEWS",
    "CONVERSION_PAGE_VISIT_CLICKS",
    "CONVERSION_PAGE_VISIT_ECPA",
    "CONVERSION_PAGE_VISIT_VIEWS",
    "COMMUNITY",
    "CLICKS",
    "CAMPAIGN_UPDATE_TIME",
    "CAMPAIGN_CREATE_TIME",
    "BID_STRATEGY",
    "DMA",
    "CONVERSION_PURCHASE_TOTAL_VALUE",
    "CONVERSION_PURCHASE_VIEWS",
    "CONVERSION_SEARCH_CLICKS",
    "CONVERSION_SEARCH_ECPA",
    "CONVERSION_SEARCH_VIEWS",
    "CONVERSION_SIGN_UP_CLICKS",
    "CONVERSION_PURCHASE_AVG_VALUE",
    "CONVERSION_PURCHASE_CLICKS",
    "CONVERSION_PURCHASE_ECPA",
    "CONVERSION_PURCHASE_TOTAL_ITEMS",
    "CONVERSION_SIGN_UP_ECPA",
]


def _report_body(starts_at: str, ends_at: str) -> dict:
    return {
        "data": {
            "starts_at": starts_at,
            "ends_at": ends_at,
            "fields": _FIELDS,
            "breakdowns": ["campaign_id", "date"],
            "time_zone_id": "GMT",
        }
    }


def _metric_rows(start: str, end: str) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "data": {
                    "metrics": [
                        {"campaign_id": "campaign-1", "date": start[:10], "impressions": 11},
                        {"campaign_id": "campaign-2", "date": end[:10], "impressions": 22},
                    ]
                }
            }
        ),
        status_code=200,
    )


def _mock_token(http_mocker: HttpMocker, response: HttpResponse | None = None) -> HttpRequest:
    request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
    http_mocker.post(
        request,
        response or HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
    )
    return request


def _report_record(breakdowns: list[str], report_date: str, identifier: str) -> dict:
    # Report rows are keyed by the lowercased requested breakdowns; the real row key of AD_ACCOUNT_ID is unverified.
    return {**{breakdown.lower(): identifier for breakdown in breakdowns}, "date": report_date}


def _hourly_report(inclusive_end: bool):
    # One row per UTC date; impressions = hours of that date inside [starts_at, ends_at), or [starts_at, ends_at] when inclusive.
    def callback(request, context) -> str:
        body = request.json()["data"]
        hour = datetime.strptime(body["starts_at"], "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(body["ends_at"], "%Y-%m-%dT%H:%M:%SZ")
        if end < hour:
            context.status_code = 400
            return json.dumps({"error": {"code": 400, "message": "The end date time must come after the start date time."}})
        end += timedelta(hours=inclusive_end)
        hours = Counter()
        while hour < end:
            hours[hour.date().isoformat()] += 1
            hour += timedelta(hours=1)
        context.status_code = 200
        return json.dumps(
            {
                "data": {
                    "metrics": [
                        {**_report_record(body["breakdowns"], day, "test-campaign"), "impressions": count}
                        for day, count in sorted(hours.items())
                    ]
                }
            }
        )

    return callback


def _read_report_windows(
    now: str,
    config: dict,
    state=None,
    bypass_spec_validation: bool = False,
) -> tuple[list[tuple[str, str]], list[str]]:
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.incremental).build()
    with freeze_time(now), HttpMocker() as http_mocker:
        http_mocker._mocker.post(
            _TOKEN_URL,
            json={"access_token": "test-access-token", "expires_in": 3600},
        )
        http_mocker._mocker.post(_REPORT_URL, text=_hourly_report(inclusive_end=True))
        source = get_source(config, catalog, state)
        if bypass_spec_validation:
            output = list(source.read(logging.getLogger("airbyte"), config, catalog, [state] if state is not None else None))
            errors = [message for message in output if message.type.name == "TRACE" and message.trace.type.name == "ERROR"]
            records = [message for message in output if message.record is not None]
        else:
            output = read(source, config, catalog, state=state) if state is not None else read(source, config, catalog)
            errors = output.errors
            records = output.records
        windows = sorted(
            (
                body["data"]["starts_at"],
                body["data"]["ends_at"],
            )
            for request in http_mocker._mocker.request_history
            if request.url == _REPORT_URL
            for body in [request.json()]
        )

    assert errors == []
    return windows, [message.record.data["date"] for message in records]


@freeze_time("2026-09-28T00:00:00Z")
def test_campaign_report_posts_exact_body_for_two_three_day_slices() -> None:
    config = base_config(start_time="2026-09-23T00:00:00Z")
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.incremental).build()
    source = get_source(config, catalog)
    first_start = "2026-09-23T00:00:00Z"
    first_end = "2026-09-26T00:00:00Z"
    second_start = "2026-09-26T00:00:00Z"
    second_end = "2026-09-28T00:00:00Z"

    with HttpMocker() as http_mocker:
        first_request = HttpRequest(_REPORT_URL, body=_report_body(first_start, first_end))
        second_request = HttpRequest(_REPORT_URL, body=_report_body(second_start, second_end))
        http_mocker.post(first_request, _metric_rows(first_start, first_end))
        http_mocker.post(second_request, _metric_rows(second_start, second_end))
        token_request = _mock_token(http_mocker)
        output = read(source, config, catalog)

    assert output.errors == []
    assert Counter(message.record.data["campaign_id"] for message in output.records) == Counter(["campaign-1", "campaign-1"])
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-09-26"
    http_mocker.assert_number_of_calls(token_request, 1)
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(second_request, 1)


@freeze_time("2026-09-28T00:00:00Z")
def test_campaign_report_retries_503_with_ad_account_message(monkeypatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    config = base_config(start_time="2026-09-26T00:00:00Z")
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.incremental).build()
    report_request = HttpRequest(
        _REPORT_URL,
        body=_report_body("2026-09-26T00:00:00Z", "2026-09-28T00:00:00Z"),
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            report_request,
            [
                HttpResponse(
                    body='{"error":{"message":"Failed to load ad account data"}}',
                    status_code=503,
                ),
                HttpResponse(
                    body='{"data":{"metrics":[{"campaign_id":"campaign-1","date":"2026-09-27"}]}}',
                    status_code=200,
                ),
            ],
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert [message.record.data["campaign_id"] for message in output.records] == ["campaign-1"]
    http_mocker.assert_number_of_calls(report_request, 2)


@freeze_time("2026-09-28T00:00:00Z")
def test_campaign_report_decodes_pagination_token_in_next_request() -> None:
    config = base_config(start_time="2026-09-25T00:00:00Z")
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.full_refresh).build()
    request_body = _report_body("2026-09-25T00:00:00Z", "2026-09-28T00:00:00Z")

    with HttpMocker() as http_mocker:
        first_request = HttpRequest(_REPORT_URL, body=request_body)
        next_page_request = HttpRequest(
            _REPORT_URL,
            query_params={"page.token": "abc="},
            body=request_body,
        )
        http_mocker.post(
            first_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "data": {"metrics": [{"campaign_id": "campaign-1", "date": "2026-09-26"}]},
                        "pagination": {"next_url": f"{_REPORT_URL}?page.token=abc%3D"},
                    }
                ),
                status_code=200,
            ),
        )
        http_mocker.post(
            next_page_request,
            HttpResponse(
                body='{"data":{"metrics":[{"campaign_id":"campaign-2","date":"2026-09-27"}]}}',
                status_code=200,
            ),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert [message.record.data["campaign_id"] for message in output.records] == ["campaign-1", "campaign-2"]
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(next_page_request, 1)


def test_campaign_report_requests_contiguous_windows_and_emits_each_utc_date_once() -> None:
    config = base_config(start_time="2026-10-02T05:00:00Z")
    windows, record_dates = _read_report_windows("2026-10-14T16:30:00Z", config)

    assert windows == [
        ("2026-10-02T00:00:00Z", "2026-10-05T00:00:00Z"),
        ("2026-10-05T00:00:00Z", "2026-10-08T00:00:00Z"),
        ("2026-10-08T00:00:00Z", "2026-10-11T00:00:00Z"),
        ("2026-10-11T00:00:00Z", "2026-10-14T00:00:00Z"),
        ("2026-10-14T00:00:00Z", "2026-10-14T16:00:00Z"),
    ]
    assert windows[0][0] == "2026-10-02T00:00:00Z"
    assert windows[-1][1] == "2026-10-14T16:00:00Z"
    assert all(next_start == previous_end for (_, previous_end), (next_start, _) in zip(windows, windows[1:]))
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:00:00Z", boundary) for window in windows for boundary in window)
    assert Counter(record_dates) == Counter((datetime(2026, 10, 2) + timedelta(days=offset)).date().isoformat() for offset in range(13))


def test_campaign_report_incremental_restart_uses_whole_day_lookback() -> None:
    state = StateBuilder().with_stream_state("campaign_report", {"date": "2026-10-14"}).build()
    config = base_config(start_time="2025-01-01T00:00:00Z")
    expected_default = [
        ("2026-10-07T00:00:00Z", "2026-10-10T00:00:00Z"),
        ("2026-10-10T00:00:00Z", "2026-10-13T00:00:00Z"),
        ("2026-10-13T00:00:00Z", "2026-10-15T09:00:00Z"),
    ]

    windows, _ = _read_report_windows("2026-10-15T09:30:00Z", config, state)
    assert windows == expected_default

    windows, _ = _read_report_windows(
        "2026-10-15T09:30:00Z",
        {**config, "report_lookback_window_days": 3},
        state,
    )
    assert windows == [
        ("2026-10-11T00:00:00Z", "2026-10-14T00:00:00Z"),
        ("2026-10-14T00:00:00Z", "2026-10-15T09:00:00Z"),
    ]

    windows, _ = _read_report_windows(
        "2026-10-15T09:30:00Z",
        {**config, "report_lookback_window_days": 0},
        state,
    )
    assert windows == [("2026-10-14T00:00:00Z", "2026-10-15T09:00:00Z")]

    windows, _ = _read_report_windows(
        "2026-10-15T09:30:00Z",
        {**config, "report_lookback_window_days": 30},
        state,
    )
    assert windows[0][0] == "2026-09-14T00:00:00Z"
    assert all(next_start == previous_end for (_, previous_end), (next_start, _) in zip(windows, windows[1:]))

    for invalid_value in (31, -1, True, "abc"):
        windows, _ = _read_report_windows(
            "2026-10-15T09:30:00Z",
            {**config, "report_lookback_window_days": invalid_value},
            state,
            bypass_spec_validation=True,
        )
        assert windows == expected_default

    legacy_state = StateBuilder().with_stream_state("campaign_report", {"date": "2026-10-13T00:00:00Z"}).build()
    windows, _ = _read_report_windows("2026-10-15T09:30:00Z", config, legacy_state)
    assert windows[0][0] == "2026-10-06T00:00:00Z"


def test_campaign_report_midnight_end_and_cursor_after_end() -> None:
    state = StateBuilder().with_stream_state("campaign_report", {"date": "2026-10-14"}).build()
    config = base_config(start_time="2026-10-02T00:00:00Z", report_lookback_window_days=0)
    windows, _ = _read_report_windows("2026-10-15T00:30:00Z", config, state)
    assert windows == [("2026-10-14T00:00:00Z", "2026-10-15T00:00:00Z")]

    state = StateBuilder().with_stream_state("campaign_report", {"date": "2026-10-15"}).build()
    windows, _ = _read_report_windows("2026-10-15T00:30:00Z", config, state)
    assert windows == []


def test_campaign_report_normalizes_offset_start_time_to_utc() -> None:
    config = base_config(start_time="2026-10-11T02:00:00+05:00")
    windows, _ = _read_report_windows("2026-10-13T23:30:00Z", config)
    assert windows == [
        ("2026-10-10T00:00:00Z", "2026-10-13T00:00:00Z"),
        ("2026-10-13T00:00:00Z", "2026-10-13T23:00:00Z"),
    ]


@freeze_time("2026-09-28T00:00:00Z")
def test_campaign_report_keeps_window_end_day_and_normalizes_date_with_time_suffix() -> None:
    config = base_config(start_time="2026-09-25T00:00:00Z")
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.incremental).build()
    rows = [{"campaign_id": "campaign-1", "date": f"2026-09-{day}T00:00:00Z"} for day in (25, 26, 27)]

    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(_REPORT_URL, body=_report_body("2026-09-25T00:00:00Z", "2026-09-28T00:00:00Z")),
            HttpResponse(body=json.dumps({"data": {"metrics": rows}}), status_code=200),
        )
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert [message.record.data["date"] for message in output.records] == ["2026-09-25", "2026-09-26", "2026-09-27"]
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-09-27"


def _sync(now: str, config: dict, inclusive_end: bool, state=None, stream_name: str = "campaign_report"):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with freeze_time(now), HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json={"access_token": "test-access-token", "expires_in": 3600})
        http_mocker._mocker.post(_REPORT_URL, text=_hourly_report(inclusive_end))
        output = read(get_source(config, catalog, state), config, catalog, state=state)
        windows = sorted(
            (r.json()["data"]["starts_at"], r.json()["data"]["ends_at"])
            for r in http_mocker._mocker.request_history
            if r.url == _REPORT_URL
        )
    assert output.errors == []
    rows = [(message.record.data["date"], message.record.data["impressions"]) for message in output.records]
    assert max(Counter(day for day, _ in rows).values()) == 1, f"date emitted twice in one sync: {rows}"
    return windows, dict(rows), output.state_messages[-1].state


def _days(first: int, last: int) -> dict:
    return {f"2026-10-{day:02d}": 24 for day in range(first, last + 1)}


@pytest.mark.parametrize("inclusive_end", [False, True], ids=["exclusive_ends_at", "inclusive_ends_at"])
def test_campaign_report_initial_sync_emits_every_whole_day_once(inclusive_end: bool) -> None:
    _, table, _ = _sync("2026-10-14T16:30:00Z", base_config(start_time="2026-10-02T00:00:00Z"), inclusive_end)
    assert table == {**_days(2, 13), "2026-10-14": 16 + inclusive_end}


@pytest.mark.parametrize("inclusive_end", [False, True], ids=["exclusive_ends_at", "inclusive_ends_at"])
def test_campaign_report_second_sync_from_emitted_state_rereads_whole_days(inclusive_end: bool) -> None:
    config = base_config(start_time="2026-10-02T00:00:00Z")
    _, _, state = _sync("2026-10-14T16:30:00Z", config, inclusive_end)
    windows, table, _ = _sync("2026-10-15T09:30:00Z", config, inclusive_end, state=[state])
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00Z", start) for start, _ in windows)
    assert table == {**_days(7, 14), "2026-10-15": 9 + inclusive_end}
