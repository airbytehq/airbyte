#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from pendulum import duration
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams import (
    AdSets,
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
)
from source_facebook_marketing.streams.base_streams import FBMarketingStream
from source_facebook_marketing.streams.streams import fetch_thumbnail_data_url


def test_filter_all_statuses(api, mocker, some_config):
    mocker.patch.multiple(FBMarketingStream, __abstractmethods__=set())
    expected = {}
    assert FBMarketingStream(api=api, account_ids=some_config["account_ids"])._filter_all_statuses() == expected

    expected = {
        "filtering": [
            {
                "field": "adset.effective_status",
                "operator": "IN",
                "value": [
                    "ACTIVE",
                    "ARCHIVED",
                    "CAMPAIGN_PAUSED",
                    "DELETED",
                    "IN_PROCESS",
                    "PAUSED",
                    "WITH_ISSUES",
                ],
            }
        ]
    }
    assert (
        AdSets(
            account_ids=some_config["account_ids"],
            start_date="",
            end_date="",
            api=api,
            filter_statuses=[
                "ACTIVE",
                "ARCHIVED",
                "CAMPAIGN_PAUSED",
                "DELETED",
                "IN_PROCESS",
                "PAUSED",
                "WITH_ISSUES",
            ],
        )._filter_all_statuses()
        == expected
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://graph.facebook.com",
        "https://graph.facebook.com?test=123%23%24%25%2A&test2=456",
        "https://graph.facebook.com?",
    ],
)
def test_fetch_thumbnail_data_url(url, requests_mock):
    requests_mock.get(url, status_code=200, headers={"content-type": "content-type"}, content=b"")
    assert fetch_thumbnail_data_url(url) == "data:content-type;base64,"


def test_parse_call_rate_header():
    headers = {
        "x-business-use-case-usage": '{"test":[{"type":"ads_management","call_count":1,"total_cputime":1,'
        '"total_time":1,"estimated_time_to_regain_access":1}]}'
    }
    assert MyFacebookAdsApi._parse_call_rate_header(headers) == (1, duration(minutes=1))


@pytest.mark.parametrize(
    "class_name, breakdowns, action_breakdowns",
    [
        [AdsInsights, [], ["action_type", "action_target_id", "action_destination"]],
        [AdsInsightsActionType, [], ["action_type"]],
        [
            AdsInsightsAgeAndGender,
            ["age", "gender"],
            ["action_type", "action_target_id", "action_destination"],
        ],
        [
            AdsInsightsCountry,
            ["country"],
            ["action_type", "action_target_id", "action_destination"],
        ],
        [
            AdsInsightsDma,
            ["dma"],
            ["action_type", "action_target_id", "action_destination"],
        ],
        [
            AdsInsightsPlatformAndDevice,
            ["publisher_platform", "platform_position", "impression_device"],
            ["action_type"],
        ],
        [
            AdsInsightsRegion,
            ["region"],
            ["action_type", "action_target_id", "action_destination"],
        ],
    ],
)
def test_ads_insights_breakdowns(class_name, breakdowns, action_breakdowns, some_config):
    kwargs = {
        "api": None,
        "account_ids": some_config["account_ids"],
        "start_date": pendulum.now(),
        "end_date": pendulum.now(),
        "insights_lookback_window": 1,
    }
    stream = class_name(**kwargs)
    assert stream.breakdowns == breakdowns
    assert stream.action_breakdowns == action_breakdowns


def test_custom_ads_insights_breakdowns(some_config):
    kwargs = {
        "api": None,
        "account_ids": some_config["account_ids"],
        "start_date": pendulum.now(),
        "end_date": pendulum.now(),
        "insights_lookback_window": 1,
    }
    stream = AdsInsights(breakdowns=["mmm"], action_breakdowns=["action_destination"], **kwargs)
    assert stream.breakdowns == ["mmm"]
    assert stream.action_breakdowns == ["action_destination"]

    stream = AdsInsights(breakdowns=[], action_breakdowns=[], **kwargs)
    assert stream.breakdowns == []
    assert stream.action_breakdowns == [
        "action_type",
        "action_target_id",
        "action_destination",
    ]

    stream = AdsInsights(breakdowns=[], action_breakdowns=[], action_breakdowns_allow_empty=True, **kwargs)
    assert stream.breakdowns == []
    assert stream.action_breakdowns == []


def test_custom_ads_insights_action_report_times(some_config):
    kwargs = {
        "api": None,
        "account_ids": some_config["account_ids"],
        "start_date": pendulum.now(),
        "end_date": pendulum.now(),
        "insights_lookback_window": 1,
        "action_breakdowns": ["action_destination"],
        "breakdowns": [],
    }
    stream = AdsInsights(**kwargs)
    assert stream.action_report_time == "mixed"

    stream = AdsInsights(action_report_time="conversion", **kwargs)
    assert stream.action_report_time == "conversion"

    stream = AdsInsights(action_report_time="impression", **kwargs)
    assert stream.action_report_time == "impression"
