#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing import SourceFacebookMarketing
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
from source_facebook_marketing.streams.streams import AdCreativesFromAds, fetch_thumbnail_data_url

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


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
    assert MyFacebookAdsApi._parse_call_rate_header(headers) == (1, timedelta(minutes=1))


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
        "start_date": ab_datetime_now(),
        "end_date": ab_datetime_now(),
        "insights_lookback_window": 1,
    }
    stream = class_name(**kwargs)
    assert stream.breakdowns == breakdowns
    assert stream.action_breakdowns == action_breakdowns


def test_custom_ads_insights_breakdowns(some_config):
    kwargs = {
        "api": None,
        "account_ids": some_config["account_ids"],
        "start_date": ab_datetime_now(),
        "end_date": ab_datetime_now(),
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


@pytest.mark.parametrize(
    "default_ads_insights_action_breakdowns, expected_action_breakdowns",
    [
        (None, ["action_type", "action_target_id", "action_destination"]),
        ([], []),
        (["action_type", "action_destination"], ["action_type", "action_destination"]),
    ],
    ids=["should_use_default_action_breakdowns_when_not_provided_in_the_config", "empty_action_breakdowns", "overridden_action_breakdowns"],
)
def test_ads_insights_default_breakdowns_based_on_config_input(default_ads_insights_action_breakdowns, expected_action_breakdowns, config):
    if default_ads_insights_action_breakdowns is not None:
        config["default_ads_insights_action_breakdowns"] = default_ads_insights_action_breakdowns
    source = SourceFacebookMarketing()
    streams = source.streams(config)
    ads_insights_stream = [stream for stream in streams if "ads_insights" == stream.name][0]
    assert ads_insights_stream.request_params()["action_breakdowns"] == expected_action_breakdowns


@pytest.mark.parametrize(
    "exception,should_raise",
    [
        pytest.param(
            FacebookRequestError(
                message="Call was not successful",
                request_context={"method": "GET"},
                http_status=500,
                http_headers={},
                body='{"error": {"message": "An unknown error occurred", "code": 1}}',
            ),
            False,
            id="facebook_request_error_returns_none",
        ),
        pytest.param(
            TypeError("some type error"),
            False,
            id="type_error_returns_none",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Error code 1: An unknown error occurred.",
                failure_type=FailureType.system_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=500,
                    http_headers={},
                    body='{"error": {"message": "An unknown error occurred", "code": 1}}',
                ),
            ),
            False,
            id="airbyte_traced_exception_with_http_500_returns_none",
        ),
        pytest.param(
            AirbyteTracedException(
                message="The access token for this connection is invalid or corrupted.",
                internal_message="Invalid OAuth access token",
                failure_type=FailureType.config_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=400,
                    http_headers={},
                    body='{"error": {"message": "Invalid OAuth access token", "code": 190}}',
                ),
            ),
            True,
            id="airbyte_traced_exception_with_http_400_raises",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Rate limit exceeded for Facebook API.",
                failure_type=FailureType.transient_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=429,
                    http_headers={},
                    body='{"error": {"message": "Rate limit exceeded", "code": 4}}',
                ),
            ),
            True,
            id="airbyte_traced_exception_with_http_429_raises",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Service temporarily unavailable.",
                failure_type=FailureType.transient_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=503,
                    http_headers={},
                    body='{"error": {"message": "Service temporarily unavailable", "code": 2}}',
                ),
            ),
            True,
            id="airbyte_traced_exception_with_http_503_raises",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Rate limit exceeded for Facebook API.",
                failure_type=FailureType.transient_error,
            ),
            True,
            id="airbyte_traced_exception_without_wrapped_fb_error_raises",
        ),
    ],
)
def test_fetch_creative_details_handles_exceptions(api, some_config, exception, should_raise):
    """Test that _fetch_creative_details handles exceptions based on HTTP status: 500 returns None, all others raise."""
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"])

    with patch("source_facebook_marketing.streams.streams.FBAdCreative") as mock_creative_cls:
        mock_creative_instance = MagicMock()
        mock_creative_cls.return_value = mock_creative_instance
        mock_creative_instance.api_get.side_effect = exception

        if should_raise:
            with pytest.raises(AirbyteTracedException):
                stream._fetch_creative_details("12345")
        else:
            result = stream._fetch_creative_details("12345")
            assert result is None


def test_fetch_creative_details_returns_data_on_success(api, some_config):
    """Test that _fetch_creative_details returns creative data on successful API call."""
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"])
    expected_data = {"id": "12345", "name": "Test Creative", "body": "Test body"}

    with patch("source_facebook_marketing.streams.streams.FBAdCreative") as mock_creative_cls:
        mock_creative_instance = MagicMock()
        mock_creative_cls.return_value = mock_creative_instance
        mock_creative_instance.api_get.return_value = mock_creative_instance
        mock_creative_instance.export_all_data.return_value = expected_data

        result = stream._fetch_creative_details("12345")
        assert result == expected_data
