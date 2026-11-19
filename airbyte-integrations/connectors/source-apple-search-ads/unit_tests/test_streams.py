# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests covering each stream in source-apple-search-ads."""

import json
from typing import Any

import pytest
from _helpers import get_source

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.searchads.apple.com/api/v5"
_TOKEN_URL = "https://appleid.apple.com/auth/oauth2/token"
_PAGE_SIZE = 1000
_CAMPAIGN_ID = 1
_ADGROUP_ID = 11
_KEYWORD_ID = 111
_AD_ID = 1111

_CONFIG = {
    "org_id": 123456,
    "client_id": "client-id",
    "client_secret": "client-secret",
    "start_date": "2024-01-01",
    "end_date": "2024-01-03",
    "timezone": "UTC",
    "token_refresh_endpoint": f"{_TOKEN_URL}?grant_type=client_credentials&scope=searchadsorg",
    "backoff_factor": 1,
    "lookback_window": 1,
    "num_workers": 1,
}

_FIRST_DAY = ("2024-01-01", "2024-01-01")
_SECOND_DAY = ("2024-01-02", "2024-01-03")

_TOKEN_REQUEST = HttpRequest(
    url=_TOKEN_URL,
    query_params={"grant_type": "client_credentials", "scope": "searchadsorg"},
    body="grant_type=client_credentials&client_id=client-id&client_secret=client-secret",
)
_TOKEN_RESPONSE = HttpResponse(body=json.dumps({"access_token": "an-access-token", "token_type": "Bearer", "expires_in": 3600}))

# Apple requires the org context header on every Campaign Management API call.
_API_HEADERS = {"X-AP-Context": f"orgId={_CONFIG['org_id']}", "Authorization": "Bearer an-access-token"}

_REPORT_PATHS = {
    "campaigns_report_daily": "/reports/campaigns",
    "adgroups_report_daily": f"/reports/campaigns/{_CAMPAIGN_ID}/adgroups",
    "keywords_report_daily": f"/reports/campaigns/{_CAMPAIGN_ID}/keywords",
    "ads_report_daily": f"/reports/campaigns/{_CAMPAIGN_ID}/ads",
}


def _mock_token(http_mocker: HttpMocker, number_of_calls: int = 1) -> None:
    http_mocker.post(_TOKEN_REQUEST, [_TOKEN_RESPONSE] * number_of_calls)


def _list_request(path: str, offset: int | None = None) -> HttpRequest:
    query_params = {"limit": str(_PAGE_SIZE)}
    if offset is not None:
        query_params["offset"] = str(offset)
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params=query_params, headers=_API_HEADERS)


def _list_response(records: list[dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": records}))


def _report_request(stream: str, start_time: str, end_time: str, offset: int | None = None) -> HttpRequest:
    pagination = {"limit": _PAGE_SIZE}
    if offset is not None:
        pagination["offset"] = offset
    return HttpRequest(
        url=f"{_BASE_URL}{_REPORT_PATHS[stream]}",
        headers=_API_HEADERS,
        body={
            "startTime": start_time,
            "endTime": end_time,
            "granularity": "DAILY",
            "groupBy": ["countryOrRegion"],
            "timeZone": "UTC",
            "selector": {"orderBy": [{"field": "countryOrRegion", "sortOrder": "ASCENDING"}], "pagination": pagination},
        },
    )


def _report_response(rows: list[dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": {"reportingDataResponse": {"row": rows}}}))


def _report_row(country: str = "US") -> dict[str, Any]:
    return {
        "metadata": {
            "campaignId": _CAMPAIGN_ID,
            "adGroupId": _ADGROUP_ID,
            "keywordId": _KEYWORD_ID,
            "adId": _AD_ID,
            "countryOrRegion": country,
        },
        # Apple returns one entry per day under granularity for DAILY reports.
        "granularity": [{"date": "2024-01-01", "impressions": 5}],
    }


def _mock_campaigns(http_mocker: HttpMocker, campaign_ids: tuple[int, ...] = (_CAMPAIGN_ID,)) -> None:
    http_mocker.get(
        _list_request("/campaigns"),
        _list_response([{"id": campaign_id, "name": f"campaign {campaign_id}"} for campaign_id in campaign_ids]),
    )


def _mock_adgroups(http_mocker: HttpMocker) -> None:
    _mock_campaigns(http_mocker)
    http_mocker.get(_list_request(f"/campaigns/{_CAMPAIGN_ID}/adgroups"), _list_response([{"id": _ADGROUP_ID, "name": "adgroup"}]))


def _read(
    stream: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: list[AirbyteStateMessage] | None = None,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(_CONFIG, catalog=catalog, state=state), config=_CONFIG, catalog=catalog, state=state)


def _state(stream: str, cursor_value: str) -> list[AirbyteStateMessage]:
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream),
                stream_state=AirbyteStateBlob({"date": cursor_value}),
            ),
        )
    ]


def test_campaigns_extract_records_from_data_field() -> None:
    with HttpMocker() as http_mocker:
        _mock_campaigns(http_mocker, campaign_ids=(1, 2))
        _mock_token(http_mocker)

        output = _read("campaigns")

        http_mocker.assert_number_of_calls(_TOKEN_REQUEST, 1)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert not output.errors


def test_full_campaign_page_paginates_with_offset() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _list_request("/campaigns"),
            _list_response([{"id": campaign_id, "name": "campaign"} for campaign_id in range(_PAGE_SIZE)]),
        )
        second_page_request = _list_request("/campaigns", offset=_PAGE_SIZE)
        http_mocker.get(second_page_request, _list_response([{"id": _PAGE_SIZE, "name": "campaign"}]))
        _mock_token(http_mocker)

        output = _read("campaigns")

        http_mocker.assert_number_of_calls(second_page_request, 1)

    assert len(output.records) == _PAGE_SIZE + 1


def test_adgroups_request_one_partition_per_campaign() -> None:
    with HttpMocker() as http_mocker:
        _mock_campaigns(http_mocker, campaign_ids=(1, 2))
        for campaign_id in (1, 2):
            http_mocker.get(
                _list_request(f"/campaigns/{campaign_id}/adgroups"),
                _list_response([{"id": campaign_id * 10, "campaignId": campaign_id}]),
            )
        _mock_token(http_mocker)

        output = _read("adgroups")

    assert [record.record.data["id"] for record in output.records] == [10, 20]


@pytest.mark.parametrize(
    "stream, path",
    [
        pytest.param("keywords", f"/campaigns/{_CAMPAIGN_ID}/adgroups/{_ADGROUP_ID}/targetingkeywords", id="keywords"),
        pytest.param("ads", f"/campaigns/{_CAMPAIGN_ID}/adgroups/{_ADGROUP_ID}/ads", id="ads"),
    ],
)
def test_nested_streams_request_adgroup_endpoint(stream: str, path: str) -> None:
    with HttpMocker() as http_mocker:
        _mock_adgroups(http_mocker)
        nested_request = _list_request(path)
        http_mocker.get(nested_request, _list_response([{"id": _KEYWORD_ID, "adGroupId": _ADGROUP_ID}]))
        _mock_token(http_mocker)

        output = _read(stream)

        http_mocker.assert_number_of_calls(nested_request, 1)

    assert [record.record.data["id"] for record in output.records] == [_KEYWORD_ID]


@pytest.mark.parametrize("stream", list(_REPORT_PATHS), ids=list(_REPORT_PATHS))
def test_report_stream_sends_one_request_per_daily_partition(stream: str) -> None:
    with HttpMocker() as http_mocker:
        if stream != "campaigns_report_daily":
            _mock_campaigns(http_mocker)
        partition_requests = [_report_request(stream, start, end) for start, end in (_FIRST_DAY, _SECOND_DAY)]
        for request in partition_requests:
            http_mocker.post(request, _report_response([_report_row()]))
        _mock_token(http_mocker)

        output = _read(stream, SyncMode.incremental)

        for request in partition_requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert [record.record.data["date"] for record in output.records] == ["2024-01-01", "2024-01-02"]
    assert not output.errors


@pytest.mark.parametrize(
    "stream, id_field, id_value",
    [
        pytest.param("campaigns_report_daily", "campaignId", _CAMPAIGN_ID, id="campaigns_report_daily"),
        pytest.param("adgroups_report_daily", "adGroupId", _ADGROUP_ID, id="adgroups_report_daily"),
        pytest.param("keywords_report_daily", "keywordId", _KEYWORD_ID, id="keywords_report_daily"),
        pytest.param("ads_report_daily", "adId", _AD_ID, id="ads_report_daily"),
    ],
)
def test_report_records_add_id_date_and_country(stream: str, id_field: str, id_value: int) -> None:
    with HttpMocker() as http_mocker:
        if stream != "campaigns_report_daily":
            _mock_campaigns(http_mocker)
        http_mocker.post(_report_request(stream, *_FIRST_DAY), _report_response([_report_row(country="FR")]))
        http_mocker.post(_report_request(stream, *_SECOND_DAY), _report_response([]))
        _mock_token(http_mocker)

        output = _read(stream, SyncMode.incremental)

    record = output.records[0].record.data
    assert record[id_field] == id_value
    assert record["date"] == "2024-01-01"
    assert record["countryorregion"] == "FR"
    assert record["granularity"] == [{"date": "2024-01-01", "impressions": 5}]


def test_full_report_page_paginates_with_offset_in_selector() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _report_request("campaigns_report_daily", *_FIRST_DAY),
            _report_response([_report_row(country=f"country {index}") for index in range(_PAGE_SIZE)]),
        )
        second_page_request = _report_request("campaigns_report_daily", *_FIRST_DAY, offset=_PAGE_SIZE)
        http_mocker.post(second_page_request, _report_response([_report_row(country="last")]))
        http_mocker.post(_report_request("campaigns_report_daily", *_SECOND_DAY), _report_response([]))
        _mock_token(http_mocker)

        output = _read("campaigns_report_daily", SyncMode.incremental)

        http_mocker.assert_number_of_calls(second_page_request, 1)

    assert len(output.records) == _PAGE_SIZE + 1


def test_report_read_emits_latest_cursor_state() -> None:
    with HttpMocker() as http_mocker:
        for start_time, end_time in (_FIRST_DAY, _SECOND_DAY):
            http_mocker.post(
                _report_request("campaigns_report_daily", start_time, end_time),
                _report_response([_report_row()]),
            )
        _mock_token(http_mocker)

        output = _read("campaigns_report_daily", SyncMode.incremental)

    assert output.most_recent_state.stream_state.date == "2024-01-02"


def test_report_read_resumes_from_cursor_minus_lookback_window() -> None:
    with HttpMocker() as http_mocker:
        remaining_request = _report_request("campaigns_report_daily", *_SECOND_DAY)
        http_mocker.post(remaining_request, _report_response([_report_row()]))
        _mock_token(http_mocker)

        output = _read(
            "campaigns_report_daily",
            SyncMode.incremental,
            state=_state("campaigns_report_daily", "2024-01-03"),
        )

        http_mocker.assert_number_of_calls(remaining_request, 1)

    assert len(output.records) == 1
    assert not output.errors


def test_report_request_defaults_timezone_and_optional_config_values() -> None:
    config = {
        "org_id": 123456,
        "client_id": "client-id",
        "client_secret": "client-secret",
        "start_date": "2024-01-01",
        "end_date": "2024-01-03",
        "num_workers": 1,
    }
    requests = [
        _report_request("campaigns_report_daily", *_FIRST_DAY),
        _report_request("campaigns_report_daily", *_SECOND_DAY),
    ]

    with HttpMocker() as http_mocker:
        for request in requests:
            http_mocker.post(request, _report_response([]))
        _mock_token(http_mocker)

        catalog = CatalogBuilder().with_stream("campaigns_report_daily", SyncMode.incremental).build()
        output = read(
            get_source(config, catalog=catalog),
            config=config,
            catalog=catalog,
        )

        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []


def test_report_retry_uses_the_default_backoff_factor(sleeps) -> None:
    config = {key: value for key, value in _CONFIG.items() if key != "backoff_factor"}
    report_request = _report_request("campaigns_report_daily", *_FIRST_DAY)
    with HttpMocker() as http_mocker:
        http_mocker.post(report_request, [HttpResponse(body="{}", status_code=500), _report_response([_report_row()])])
        http_mocker.post(_report_request("campaigns_report_daily", *_SECOND_DAY), _report_response([]))
        _mock_token(http_mocker)

        catalog = CatalogBuilder().with_stream("campaigns_report_daily", SyncMode.incremental).build()
        output = read(get_source(config, catalog=catalog), config, catalog)

    assert len(output.records) == 1
    assert not output.errors
    # ExponentialBackoffStrategy with the default factor 5: 5 * 2**1 seconds, plus the CDK's extra second.
    assert [seconds for seconds in sleeps if seconds] == [11]
