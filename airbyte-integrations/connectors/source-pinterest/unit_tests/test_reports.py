#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import os

import pytest
from freezegun import freeze_time
from jsonschema import ValidationError, validate

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_analytics_columns, get_source, read_from_stream


os.environ["REQUEST_CACHE_PATH"] = "/tmp"


@freeze_time("2022-11-16 12:03:11+00:00")
def test_read_records(requests_mock, test_config, analytics_report_stream, date_range):
    report_download_url = "https://download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"

    final_report_status = {"report_status": "FINISHED", "url": report_download_url}

    final_response = {"campaign_id": [{"metric": 1}]}

    expected_body = {
        "start_date": "2022-11-15",
        "end_date": "2022-11-16",
        "granularity": "DAY",
        "columns": get_analytics_columns().split(","),
        "level": "CAMPAIGN",
    }

    def match_json_body(request):
        # request.body can be bytes or str; parse as JSON
        raw = request.body.decode() if isinstance(request.body, (bytes, bytearray)) else request.body
        return json.loads(raw) == expected_body

    # creation success payload
    initial_creation_ok = {"report_status": "IN_PROGRESS", "token": "token", "message": ""}

    # simulate retryable *creation* errors, then success
    creation_error_responses = [
        {  # rate limit (retryable)
            "status_code": 429,
            "json": {"code": 2726, "message": "Reporting query cost limit exceeded. Retry after 1 seconds"},
        },
        {  # server error (retryable)
            "status_code": 500,
            "json": {"message": "internal error"},
        },
        {
            "status_code": 400,
            "json": {"code": 1, "message": "Retry after 5 seconds"},
        },
        {
            "status_code": 400,
            "json": {"code": 12, "message": "Something went wrong on our end. Sorry about that."},
        },
        {  # finally succeed creating the job
            "status_code": 200,
            "json": initial_creation_ok,
        },
    ]

    # parent resource
    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})

    # creation POST with stacked responses + body validation
    requests_mock.post(
        report_request_url,
        creation_error_responses,
        additional_matcher=match_json_body,
    )
    requests_mock.get(report_request_url, json=final_report_status, status_code=200)
    requests_mock.get(report_download_url, json=final_response, status_code=200)

    state = (
        StateBuilder()
        .with_stream_state(
            "campaign_analytics_report",
            {
                "DATE": "2022-11-15",
            },
        )
        .build()
    )

    records = [
        record.record.data
        for record in read_from_stream(test_config, "campaign_analytics_report", SyncMode.incremental, state=state).records
    ]
    expected_record = {"metric": 1}

    assert records[0] == expected_record


def test_streams(test_config):
    source = get_source(test_config)
    streams = source.streams(test_config)
    expected_streams_number = 32
    assert len(streams) == expected_streams_number


@freeze_time("2022-11-16 12:03:11+00:00")
def test_read_records_refreshes_download_url_before_fetch(requests_mock, test_config):
    expired_report_download_url = "https://expired-download.report"
    fresh_report_download_url = "https://fresh-download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"
    final_response = {"campaign_id": [{"metric": 1}]}

    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.post(
        report_request_url,
        json={"report_status": "IN_PROGRESS", "token": "token", "message": ""},
        status_code=200,
    )
    requests_mock.get(
        report_request_url,
        [
            {
                "json": {"report_status": "FINISHED", "url": expired_report_download_url},
                "status_code": 200,
            },
            {
                "json": {"report_status": "FINISHED", "url": fresh_report_download_url},
                "status_code": 200,
            },
        ],
    )
    requests_mock.get(expired_report_download_url, status_code=403)
    requests_mock.get(fresh_report_download_url, json=final_response, status_code=200)

    state = (
        StateBuilder()
        .with_stream_state(
            "campaign_analytics_report",
            {
                "DATE": "2022-11-15",
            },
        )
        .build()
    )

    records = [
        record.record.data
        for record in read_from_stream(test_config, "campaign_analytics_report", SyncMode.incremental, state=state).records
    ]

    assert records == [{"metric": 1}]
    assert not requests_mock.called_once
    assert requests_mock.request_history[-1].url.rstrip("/") == fresh_report_download_url
    assert not any(request.url.rstrip("/") == expired_report_download_url for request in requests_mock.request_history)


@freeze_time("2022-11-16 12:03:11+00:00")
def test_report_rate_limit_during_download_target_refresh_retries(requests_mock, test_config):
    """Rate-limit (code=8) on download_target_requester should be retried, not ignored."""
    report_download_url = "https://download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"
    final_response = {"campaign_id": [{"metric": 1}]}

    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.post(
        report_request_url,
        json={"report_status": "IN_PROGRESS", "token": "token", "message": ""},
        status_code=200,
    )
    requests_mock.get(
        report_request_url,
        [
            {  # polling: report finished
                "json": {"report_status": "FINISHED", "url": report_download_url},
                "status_code": 200,
            },
            {  # download_target_requester hits rate limit (code=8)
                "json": {"code": 8, "message": "You have exceeded your rate limit. Try again later."},
                "status_code": 400,
                "headers": {"X-RateLimit-Reset": "0"},
            },
            {  # retry succeeds
                "json": {"report_status": "FINISHED", "url": report_download_url},
                "status_code": 200,
            },
        ],
    )
    requests_mock.get(report_download_url, json=final_response, status_code=200)

    state = (
        StateBuilder()
        .with_stream_state(
            "campaign_analytics_report",
            {"DATE": "2022-11-15"},
        )
        .build()
    )

    records = [
        record.record.data
        for record in read_from_stream(test_config, "campaign_analytics_report", SyncMode.incremental, state=state).records
    ]
    assert records == [{"metric": 1}]


def test_custom_streams(test_config):
    config = copy.deepcopy(test_config)
    config["custom_reports"] = [
        {
            "name": "vadim_report",
            "level": "AD_GROUP",
            "granularity": "MONTH",
            "click_window_days": 30,
            "engagement_window_days": 30,
            "view_window_days": 30,
            "conversion_report_time": "TIME_OF_CONVERSION",
            "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
            "columns": ["ADVERTISER_ID", "AD_ACCOUNT_ID", "AD_GROUP_ID", "CTR", "IMPRESSION_2"],
            "start_date": "2023-01-08",
        }
    ]
    source = get_source(config)
    streams = source.streams(config)
    expected_streams_number = 33
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize(
    "status_fields",
    [
        pytest.param({}, id="omitted"),
        pytest.param(
            {
                "campaign_statuses": ["RUNNING", "ARCHIVED"],
                "ad_group_statuses": ["PAUSED", "ARCHIVED"],
                "ad_statuses": ["APPROVED", "ARCHIVED"],
            },
            id="configured",
        ),
    ],
)
@freeze_time("2026-05-21 12:00:00+00:00")
def test_custom_reports_status_filters(requests_mock, test_config, status_fields):
    report_download_url = "https://download.report/custom"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"
    config = copy.deepcopy(test_config)
    config["custom_reports"] = [
        {
            "name": "ad_performance_report",
            "level": "PIN_PROMOTION",
            "granularity": "DAY",
            "columns": [
                "ADVERTISER_ID",
                "AD_ACCOUNT_ID",
                "AD_ID",
                "PIN_PROMOTION_ID",
                "SPEND_IN_DOLLAR",
            ],
            "click_window_days": 30,
            "engagement_window_days": 30,
            "view_window_days": 30,
            "conversion_report_time": "TIME_OF_AD_ACTION",
            "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
            "start_date": "2026-05-20",
            **status_fields,
        }
    ]
    expected_body = {
        "start_date": "2026-05-20",
        "end_date": "2026-05-21",
        "level": "PIN_PROMOTION",
        "granularity": "DAY",
        "click_window_days": 30,
        "engagement_window_days": 30,
        "view_window_days": 30,
        "conversion_report_time": "TIME_OF_AD_ACTION",
        "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
        "columns": [
            "ADVERTISER_ID",
            "AD_ACCOUNT_ID",
            "AD_ID",
            "PIN_PROMOTION_ID",
            "SPEND_IN_DOLLAR",
        ],
        **status_fields,
    }

    def match_json_body(request):
        raw = request.body.decode() if isinstance(request.body, (bytes, bytearray)) else request.body
        actual_body = json.loads(raw)
        assert actual_body == expected_body
        return True

    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.post(
        report_request_url,
        json={"report_status": "IN_PROGRESS", "token": "token", "message": ""},
        additional_matcher=match_json_body,
    )
    requests_mock.get(report_request_url, json={"report_status": "FINISHED", "url": report_download_url})
    requests_mock.get(report_download_url, json={"ad_id": [{"spend": 1}]})

    records = [record.record.data for record in read_from_stream(config, "custom_ad_performance_report", SyncMode.incremental).records]

    assert records == [{"spend": 1}]


@freeze_time("2026-05-21 12:00:00+00:00")
def test_custom_reports_status_filters_chunk_over_limit_values(requests_mock, test_config):
    report_download_url = "https://download.report/custom"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"
    campaign_statuses = ["RUNNING", "PAUSED", "NOT_STARTED", "COMPLETED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"]
    ad_group_statuses = ["RUNNING", "PAUSED"]
    ad_statuses = ["APPROVED", "PAUSED", "PENDING", "REJECTED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"]
    config = copy.deepcopy(test_config)
    config["custom_reports"] = [
        {
            "name": "ad_performance_report",
            "level": "PIN_PROMOTION",
            "granularity": "DAY",
            "columns": [
                "ADVERTISER_ID",
                "AD_ACCOUNT_ID",
                "AD_ID",
                "PIN_PROMOTION_ID",
                "SPEND_IN_DOLLAR",
            ],
            "click_window_days": 30,
            "engagement_window_days": 30,
            "view_window_days": 30,
            "conversion_report_time": "TIME_OF_AD_ACTION",
            "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
            "start_date": "2026-05-19",
            "campaign_statuses": campaign_statuses,
            "ad_group_statuses": ad_group_statuses,
            "ad_statuses": ad_statuses,
        }
    ]
    expected_body_base = {
        "start_date": "2026-05-20",
        "end_date": "2026-05-21",
        "level": "PIN_PROMOTION",
        "granularity": "DAY",
        "click_window_days": 30,
        "engagement_window_days": 30,
        "view_window_days": 30,
        "conversion_report_time": "TIME_OF_AD_ACTION",
        "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
        "columns": [
            "ADVERTISER_ID",
            "AD_ACCOUNT_ID",
            "AD_ID",
            "PIN_PROMOTION_ID",
            "SPEND_IN_DOLLAR",
        ],
    }
    actual_bodies = []

    def match_json_body(request):
        raw = request.body.decode() if isinstance(request.body, (bytes, bytearray)) else request.body
        actual_body = json.loads(raw)
        actual_bodies.append(actual_body)
        assert {key: value for key, value in actual_body.items() if not key.endswith("_statuses")} == expected_body_base
        assert 1 <= len(actual_body["campaign_statuses"]) <= 6
        assert 1 <= len(actual_body["ad_group_statuses"]) <= 6
        assert 1 <= len(actual_body["ad_statuses"]) <= 6
        return True

    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.post(
        report_request_url,
        json={"report_status": "IN_PROGRESS", "token": "token", "message": ""},
        additional_matcher=match_json_body,
    )
    requests_mock.get(report_request_url, json={"report_status": "FINISHED", "url": report_download_url})
    requests_mock.get(report_download_url, json={"ad_id": [{"spend": 1}]})

    state = (
        StateBuilder()
        .with_stream_state(
            "custom_ad_performance_report",
            {
                "DATE": "2026-05-20",
            },
        )
        .build()
    )

    records = [
        record.record.data for record in read_from_stream(config, "custom_ad_performance_report", SyncMode.incremental, state=state).records
    ]

    assert records == [{"spend": 1}, {"spend": 1}, {"spend": 1}, {"spend": 1}]
    assert len(actual_bodies) == 4
    assert {tuple(body["campaign_statuses"]) for body in actual_bodies} == {
        tuple(campaign_statuses[:6]),
        tuple(campaign_statuses[6:]),
    }
    assert {tuple(body["ad_group_statuses"]) for body in actual_bodies} == {tuple(ad_group_statuses)}
    assert {tuple(body["ad_statuses"]) for body in actual_bodies} == {
        tuple(ad_statuses[:6]),
        tuple(ad_statuses[6:]),
    }


@pytest.mark.parametrize(
    "field_name,valid_statuses,invalid_statuses",
    [
        pytest.param(
            "campaign_statuses",
            ["RUNNING", "PAUSED", "NOT_STARTED", "COMPLETED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"],
            ["RUNNING", "RUNNING"],
            id="campaign_statuses",
        ),
        pytest.param(
            "ad_group_statuses",
            ["RUNNING", "PAUSED", "NOT_STARTED", "COMPLETED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"],
            ["RUNNING", "RUNNING"],
            id="ad_group_statuses",
        ),
        pytest.param(
            "ad_statuses",
            ["APPROVED", "PAUSED", "PENDING", "REJECTED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"],
            ["APPROVED", "APPROVED"],
            id="ad_statuses",
        ),
    ],
)
def test_custom_report_status_filters_allow_more_than_six_values(test_config, field_name, valid_statuses, invalid_statuses):
    status_schema = (
        get_source(test_config).spec(None).connectionSpecification["properties"]["custom_reports"]["items"]["properties"][field_name]
    )

    validate(valid_statuses, status_schema)
    with pytest.raises(ValidationError):
        validate(invalid_statuses, status_schema)
