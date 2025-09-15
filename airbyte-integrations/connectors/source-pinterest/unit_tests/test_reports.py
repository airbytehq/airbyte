#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import os
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from source_pinterest import SourcePinterest
from source_pinterest.reports.reports import (
    AdGroupTargetingReport,
    AdvertiserTargetingReport,
    CampaignTargetingReport,
    KeywordReport,
    PinPromotionTargetingReport,
    ProductGroupTargetingReport,
)
from source_pinterest.utils import get_analytics_columns

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import read_from_stream


os.environ["REQUEST_CACHE_PATH"] = "/tmp"


@freeze_time("2022-11-16 12:03:11+00:00")
def test_read_records(requests_mock, test_config, analytics_report_stream, date_range):
    report_download_url = "https://download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"

    final_report_status = {"report_status": "FINISHED", "url": report_download_url}

    initial_response = {"report_status": "IN_PROGRESS", "token": "token", "message": ""}

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
        {  # 400 treated as retryable by your error handler
            "status_code": 400,
            "json": {"code": 1, "message": "transient creation error"},
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
    source = SourcePinterest(None, test_config, None)
    streams = source.streams(test_config)
    expected_streams_number = 32
    assert len(streams) == expected_streams_number


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
    source = SourcePinterest(None, config, None)
    streams = source.streams(config)
    expected_streams_number = 33
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize(
    ("report_name", "expected_level"),
    (
        [CampaignTargetingReport, "CAMPAIGN_TARGETING"],
        [AdvertiserTargetingReport, "ADVERTISER_TARGETING"],
        [AdGroupTargetingReport, "AD_GROUP_TARGETING"],
        [PinPromotionTargetingReport, "PIN_PROMOTION_TARGETING"],
        [ProductGroupTargetingReport, "PRODUCT_GROUP_TARGETING"],
        [KeywordReport, "KEYWORD"],
    ),
)
def test_level(test_config, report_name, expected_level):
    assert report_name(parent=None, config=MagicMock()).level == expected_level
