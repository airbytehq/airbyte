# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import base_config, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


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


@freeze_time("2026-09-28T00:00:00Z")
def test_campaign_report_posts_exact_body_for_two_three_day_slices() -> None:
    config = base_config(start_time="2026-09-23T00:00:00Z")
    catalog = CatalogBuilder().with_stream("campaign_report", SyncMode.incremental).build()
    source = get_source(config, catalog)
    first_start = "2026-09-23T00:00:00Z"
    first_end = "2026-09-25T00:00:00Z"
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
    assert [message.record.data["campaign_id"] for message in output.records] == [
        "campaign-1",
        "campaign-2",
        "campaign-1",
        "campaign-2",
    ]
    assert output.state_messages[-1].state.stream.stream_state.date == "2026-09-28T00:00:00Z"
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
