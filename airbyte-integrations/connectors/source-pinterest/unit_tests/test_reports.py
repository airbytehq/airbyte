#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import os
from unittest.mock import MagicMock

import pytest
import responses
from source_pinterest import SourcePinterest
from source_pinterest.reports import CampaignAnalyticsReport
from source_pinterest.reports.reports import (
    AdGroupReport,
    AdGroupTargetingReport,
    AdvertiserReport,
    AdvertiserTargetingReport,
    CampaignTargetingReport,
    KeywordReport,
    PinPromotionReport,
    PinPromotionTargetingReport,
    ProductGroupReport,
    ProductGroupTargetingReport,
    ProductItemReport,
)
from source_pinterest.utils import get_analytics_columns
from unit_tests.test_source import setup_responses

os.environ["REQUEST_CACHE_PATH"] = '/tmp'

@responses.activate
def test_request_body_json(analytics_report_stream, date_range):
    granularity = "DAY"
    columns = get_analytics_columns()

    expected_body = {
        "start_date": date_range["start_date"],
        "end_date": date_range["end_date"],
        "granularity": granularity,
        "columns": columns.split(","),
        "level": analytics_report_stream.level,
    }

    body = analytics_report_stream.request_body_json(date_range)
    assert body == expected_body


@responses.activate
def test_read_records(analytics_report_stream, date_range):
    report_download_url = "https://download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"

    final_report_status = {"report_status": "FINISHED", "url": report_download_url}

    initial_response = {"report_status": "IN_PROGRESS", "token": "token", "message": ""}

    final_response = {"campaign_id": [{"metric": 1}]}

    responses.add(responses.POST, report_request_url, json=initial_response)
    responses.add(responses.GET, report_request_url, json=final_report_status, status=200)
    responses.add(responses.GET, report_download_url, json=final_response, status=200)

    sync_mode = "full_refresh"
    cursor_field = ["last_updated"]
    stream_state = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
    }

    records = analytics_report_stream.read_records(sync_mode, cursor_field, date_range, stream_state)
    expected_record = {"metric": 1}

    assert next(records) == expected_record
    assert len(responses.calls) == 3
    assert responses.calls[0].request.url == report_request_url


@responses.activate
def test_streams(test_config):
    setup_responses()
    source = SourcePinterest()
    streams = source.streams(test_config)
    expected_streams_number = 32
    assert len(streams) == expected_streams_number

@responses.activate
def test_custom_streams(test_config):
    config = copy.deepcopy(test_config)
    config['custom_reports'] = [{
        "name": "vadim_report",
        "level": "AD_GROUP",
        "granularity": "MONTH",
        "click_window_days": 30,
        "engagement_window_days": 30,
        "view_window_days": 30,
        "conversion_report_time": "TIME_OF_CONVERSION",
        "attribution_types": ["INDIVIDUAL", "HOUSEHOLD"],
        "columns": ["ADVERTISER_ID", "AD_ACCOUNT_ID", "AD_GROUP_ID", "CTR", "IMPRESSION_2"],
        "start_date": "2023-01-08"
    }]
    setup_responses()
    source = SourcePinterest()
    streams = source.streams(config)
    expected_streams_number = 33
    assert len(streams) == expected_streams_number

@pytest.mark.parametrize(
    "report_name, expected_level",
    [
        [CampaignAnalyticsReport, 'CAMPAIGN'],
        [CampaignTargetingReport, 'CAMPAIGN_TARGETING'],
        [AdvertiserReport, 'ADVERTISER'],
        [AdvertiserTargetingReport, 'ADVERTISER_TARGETING'],
        [AdGroupReport, 'AD_GROUP'],
        [AdGroupTargetingReport, 'AD_GROUP_TARGETING'],
        [PinPromotionReport, 'PIN_PROMOTION'],
        [PinPromotionTargetingReport, 'PIN_PROMOTION_TARGETING'],
        [ProductGroupReport, 'PRODUCT_GROUP'],
        [ProductGroupTargetingReport, 'PRODUCT_GROUP_TARGETING'],
        [ProductItemReport, 'PRODUCT_ITEM'],
        [KeywordReport, 'KEYWORD']
    ],
)
def test_level(test_config, report_name, expected_level):
    assert report_name(parent=None, config=MagicMock()).level == expected_level

