#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

import pytest
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from facebook_business.session import FacebookSession
from source_facebook_marketing import SourceFacebookMarketing
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams import (
    AdCreatives,
    AdSets,
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsComscoreMarket,
    AdsInsightsCountry,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
)
from source_facebook_marketing.streams.base_streams import FBMarketingStream
from source_facebook_marketing.streams.streams import AdAccount, AdCreativesFromAds, fetch_thumbnail_data_url

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


def test_ad_creatives_from_ads_schema_scopes_parent_updated_time(api, some_config):
    direct_stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    ads_stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
    )

    assert "updated_time" not in direct_stream.get_json_schema()["properties"]
    assert "updated_time" in ads_stream.get_json_schema()["properties"]


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
            AdsInsightsComscoreMarket,
            ["comscore_market"],
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
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)

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
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    expected_data = {"id": "12345", "name": "Test Creative", "body": "Test body"}

    with patch("source_facebook_marketing.streams.streams.FBAdCreative") as mock_creative_cls:
        mock_creative_instance = MagicMock()
        mock_creative_cls.return_value = mock_creative_instance
        mock_creative_instance.api_get.return_value = mock_creative_instance
        mock_creative_instance.export_all_data.return_value = expected_data

        result = stream._fetch_creative_details("12345")
        assert result == expected_data


def test_ad_creatives_from_ads_request_params_include_status_and_cursor_filters(api, some_config):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
        filter_statuses=["ACTIVE"],
    )

    params = stream.request_params(stream_state={"updated_time": "2021-01-23T00:00:00+00:00", "filter_statuses": ["ACTIVE"]})

    assert params["filtering"] == [
        {
            "field": "ad.effective_status",
            "operator": "IN",
            "value": ["ACTIVE"],
        },
        {
            "field": "ad.updated_time",
            "operator": "GREATER_THAN",
            "value": 1611360000,
        },
    ]


def test_ad_creatives_from_ads_request_params_skip_cursor_on_first_sync_without_start_date(api, some_config):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
        filter_statuses=["ACTIVE"],
    )

    assert stream.request_params(stream_state={}) == {
        "limit": 100,
        "filtering": [
            {
                "field": "ad.effective_status",
                "operator": "IN",
                "value": ["ACTIVE"],
            }
        ],
    }


def test_ad_creatives_from_ads_request_params_skip_cursor_on_first_sync_with_start_date(api, some_config):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=datetime(2021, 2, 1, tzinfo=timezone.utc),
        end_date=None,
        filter_statuses=["ACTIVE"],
    )

    assert stream.request_params(stream_state={}) == {
        "limit": 100,
        "filtering": [
            {
                "field": "ad.effective_status",
                "operator": "IN",
                "value": ["ACTIVE"],
            }
        ],
    }


def test_ad_creatives_from_ads_request_params_use_state_cursor_over_start_date(api, some_config):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=datetime(2021, 2, 1, tzinfo=timezone.utc),
        end_date=None,
        filter_statuses=["ACTIVE"],
    )

    params = stream.request_params(stream_state={"updated_time": "2021-01-23T00:00:00+00:00", "filter_statuses": ["ACTIVE"]})

    assert params["filtering"] == [
        {
            "field": "ad.effective_status",
            "operator": "IN",
            "value": ["ACTIVE"],
        },
        {
            "field": "ad.updated_time",
            "operator": "GREATER_THAN",
            "value": 1611360000,
        },
    ]


def test_ad_creatives_from_ads_full_refresh_ignores_state_cursor(api, some_config, mocker):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
        filter_statuses=["ACTIVE"],
    )
    list_objects = mocker.patch.object(stream, "list_objects", return_value=iter([]))

    list(
        stream.read_records(
            sync_mode=SyncMode.full_refresh,
            stream_slice={
                "account_id": some_config["account_ids"][0],
                "stream_state": {
                    "updated_time": "2021-01-23T00:00:00+00:00",
                    "filter_statuses": ["ACTIVE"],
                },
            },
            stream_state={
                "updated_time": "2021-01-23T00:00:00+00:00",
                "filter_statuses": ["ACTIVE"],
            },
        )
    )

    assert list_objects.call_args.kwargs["params"] == {
        "limit": 100,
        "filtering": [
            {
                "field": "ad.effective_status",
                "operator": "IN",
                "value": ["ACTIVE"],
            }
        ],
    }


def test_ad_creatives_from_ads_emits_parent_updated_time_and_advances_state(api, some_config, mocker):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
    )
    parent_ads = [
        {
            "id": "ad-1",
            "creative": {"id": "creative-1"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": some_config["account_ids"][0],
        },
        {
            "id": "ad-2",
            "creative": {"id": "creative-2"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": some_config["account_ids"][0],
        },
        {
            "id": "ad-3",
            "creative": {"id": "creative-1"},
            "updated_time": "2021-01-24T00:00:00+00:00",
            "account_id": some_config["account_ids"][0],
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(
        stream,
        "_fetch_creative_details",
        side_effect=lambda creative_id: {"id": creative_id},
    )

    records = list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": some_config["account_ids"][0], "stream_state": {}},
            stream_state={},
        )
    )

    assert records == [
        {"id": "creative-1", "updated_time": "2021-01-23T00:00:00+00:00", "account_id": some_config["account_ids"][0]},
        {"id": "creative-2", "updated_time": "2021-01-25T00:00:00+00:00", "account_id": some_config["account_ids"][0]},
    ]
    assert stream.state[some_config["account_ids"][0]]["updated_time"] == "2021-01-25T00:00:00+00:00"


def test_ad_creatives_from_ads_parent_without_updated_time_does_not_crash(api, some_config, mocker):
    stream = AdCreativesFromAds(
        api=api,
        account_ids=some_config["account_ids"],
        start_date=None,
        end_date=None,
    )
    parent_ads = [{"id": "ad-1", "creative": {"id": "creative-1"}}]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", return_value={"id": "creative-1"})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": some_config["account_ids"][0], "stream_state": {}},
            stream_state={},
        )
    )

    assert records[0]["updated_time"] is None
    assert stream.state == {}


def test_ad_creatives_from_ads_failed_fetch_does_not_advance_past_failed_cursor(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-success-before-failure",
            "creative": {"id": "creative-success-before-failure"},
            "updated_time": "2021-01-22T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-success-after-failure",
            "creative": {"id": "creative-success-after-failure"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-failure",
            "creative": {"id": "creative-failure"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(
        stream,
        "_fetch_creative_details",
        side_effect=[
            {"id": "creative-success-before-failure"},
            {"id": "creative-success-after-failure"},
            None,
        ],
    )

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # The latest success (01-25) sits after the failure, so the cursor rewinds to one second before it.
    assert stream.state[account_id]["updated_time"] == "2021-01-22T23:59:59+00:00"


def test_ad_creatives_from_ads_all_failed_fetches_leave_state_untouched(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-failure-1",
            "creative": {"id": "creative-failure-1"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-failure-2",
            "creative": {"id": "creative-failure-2"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", return_value=None)

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    assert stream.state == {}


def test_ad_creatives_from_ads_repeated_failed_creative_remains_a_failure(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-success",
            "creative": {"id": "creative-success"},
            "updated_time": "2021-01-22T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-failure",
            "creative": {"id": "creative-failure"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-repeated-failure",
            "creative": {"id": "creative-failure"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    fetch_creative_details = mocker.patch.object(
        stream,
        "_fetch_creative_details",
        side_effect=[{"id": "creative-success"}, None],
    )

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    fetch_creative_details.assert_has_calls([mocker.call("creative-success"), mocker.call("creative-failure")])
    assert fetch_creative_details.call_count == 2
    assert stream.state[account_id]["updated_time"] == "2021-01-22T00:00:00+00:00"


def test_ad_creatives_from_ads_ad_without_creative_does_not_hold_cursor_back(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-without-creative",
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-success",
            "creative": {"id": "creative-success"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", return_value={"id": "creative-success"})

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    assert stream.state[account_id]["updated_time"] == "2021-01-23T00:00:00+00:00"


def test_ad_creatives_from_ads_success_equal_to_failed_cursor_rewinds_before_failure(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-success",
            "creative": {"id": "creative-success"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-failure",
            "creative": {"id": "creative-failure"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", side_effect=[{"id": "creative-success"}, None])

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # Checkpointing the shared timestamp would filter the failed creative out of the next sync forever, so the
    # cursor must land strictly before it. The GREATER_THAN filter then re-reads both ads at 2021-01-23.
    assert stream.state[account_id]["updated_time"] == "2021-01-22T23:59:59+00:00"


def test_ad_creatives_from_ads_failed_ad_without_cursor_blocks_checkpointing(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-success",
            "creative": {"id": "creative-success"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-failure-without-updated-time",
            "creative": {"id": "creative-failure"},
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", side_effect=[{"id": "creative-success"}, None])

    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # A failed creative with no cursor cannot be placed on the timeline, so no cursor is safe to checkpoint.
    assert stream.state == {}


def test_ad_creatives_from_ads_re_referenced_successful_creative_advances_cursor(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-1",
            "creative": {"id": "creative-1"},
            "updated_time": "2021-01-20T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-2",
            "creative": {"id": "creative-2"},
            "updated_time": "2021-01-24T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-3",
            "creative": {"id": "creative-1"},
            "updated_time": "2021-01-28T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", side_effect=lambda creative_id: {"id": creative_id})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # ad-3 is deduplicated away, but it is the only source of the slice's latest cursor.
    assert [record["id"] for record in records] == ["creative-1", "creative-2"]
    assert stream.state[account_id]["updated_time"] == "2021-01-28T00:00:00+00:00"


@pytest.mark.parametrize("sync_mode", ["full_refresh", SyncMode.full_refresh], ids=["string", "enum"])
def test_ad_creatives_from_ads_full_refresh_does_not_advance_state(api, some_config, mocker, sync_mode):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-1",
            "creative": {"id": "creative-1"},
            "updated_time": "2021-01-23T00:00:00+00:00",
            "account_id": account_id,
        },
        {
            "id": "ad-2",
            "creative": {"id": "creative-2"},
            "updated_time": "2021-01-25T00:00:00+00:00",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", side_effect=lambda creative_id: {"id": creative_id})

    records = list(
        stream.read_records(
            sync_mode=sync_mode,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # The CDK checkpoints whatever state the stream exposes, so a full refresh must not publish a cursor:
    # a retried attempt would otherwise resume filtered and silently return a partial full refresh.
    assert len(records) == 2
    assert stream.state == {}


def test_ad_creatives_from_ads_unparsable_updated_time_is_treated_as_missing(api, some_config, mocker):
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    account_id = some_config["account_ids"][0]
    parent_ads = [
        {
            "id": "ad-malformed",
            "creative": {"id": "creative-1"},
            "updated_time": "not-a-date",
            "account_id": account_id,
        },
    ]
    mocker.patch("source_facebook_marketing.streams.base_streams.FBMarketingStream.read_records", return_value=iter(parent_ads))
    mocker.patch.object(stream, "_fetch_creative_details", return_value={"id": "creative-1"})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account_id": account_id, "stream_state": {}},
            stream_state={},
        )
    )

    # A malformed timestamp from the API must not abort the account slice; the record is still emitted and the
    # unusable cursor is simply never checkpointed.
    assert [record["id"] for record in records] == ["creative-1"]
    assert stream.state == {}


@pytest.mark.parametrize(
    "exception,expected_behavior,expected_raise_type",
    [
        pytest.param(
            FacebookRequestError(
                message="Call was not successful",
                request_context={"method": "GET"},
                http_status=400,
                http_headers={},
                body='{"error": {"message": "(#200) Requires business_management permission to manage the object", "code": 200}}',
            ),
            "remove_owner",
            None,
            id="fb_error_owner_permission_removes_owner",
        ),
        pytest.param(
            FacebookRequestError(
                message="Call was not successful",
                request_context={"method": "GET"},
                http_status=400,
                http_headers={},
                body='{"error": {"message": "Unsupported request - method type: get", "code": 100}}',
            ),
            "remove_funding_source_details",
            None,
            id="fb_error_funding_source_removes_field",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Credentials don't have enough permissions.",
                failure_type=FailureType.config_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=400,
                    http_headers={},
                    body='{"error": {"message": "(#200) Requires business_management permission to manage the object", "code": 200}}',
                ),
            ),
            "remove_owner",
            None,
            id="airbyte_traced_wrapping_owner_permission_error_removes_owner",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Error code 100: Unsupported request - method type: get.",
                failure_type=FailureType.system_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=400,
                    http_headers={},
                    body='{"error": {"message": "Unsupported request - method type: get", "code": 100}}',
                ),
            ),
            "remove_funding_source_details",
            None,
            id="airbyte_traced_wrapping_funding_source_error_removes_field",
        ),
        pytest.param(
            AirbyteTracedException(
                message="The access token for this connection is invalid or corrupted.",
                failure_type=FailureType.config_error,
                exception=FacebookRequestError(
                    message="Call was not successful",
                    request_context={"method": "GET"},
                    http_status=400,
                    http_headers={},
                    body='{"error": {"message": "Invalid OAuth access token", "code": 190}}',
                ),
            ),
            "raise",
            FacebookRequestError,
            id="airbyte_traced_wrapping_unrelated_fb_error_raises",
        ),
        pytest.param(
            AirbyteTracedException(
                message="Some unrelated error.",
                failure_type=FailureType.system_error,
            ),
            "raise",
            AirbyteTracedException,
            id="airbyte_traced_without_wrapped_fb_error_raises",
        ),
        pytest.param(
            FacebookRequestError(
                message="Call was not successful",
                request_context={"method": "GET"},
                http_status=400,
                http_headers={},
                body='{"error": {"message": "Invalid OAuth access token", "code": 190}}',
            ),
            "raise",
            FacebookRequestError,
            id="fb_error_unrelated_raises",
        ),
    ],
)
def test_ad_account_list_objects_handles_facebook_and_traced_exceptions(
    api, some_config, exception, expected_behavior, expected_raise_type
):
    """Test that AdAccount.list_objects handles FacebookRequestError and AirbyteTracedException
    wrapping FacebookRequestError for the owner permission and funding_source_details errors,
    and re-raises all others."""
    stream = AdAccount(api=api, account_ids=some_config["account_ids"])
    account_id = some_config["account_ids"][0]

    with (
        patch.object(stream, "fields", return_value=["owner", "funding_source_details", "id"]),
        patch("source_facebook_marketing.streams.streams.FBAdAccount") as mock_fb_account,
    ):
        mock_account_instance = MagicMock()
        mock_fb_account.return_value = mock_account_instance
        # First call raises the exception; second call (after field removal) succeeds
        mock_account_instance.api_get.side_effect = [exception, MagicMock()]

        if expected_behavior == "raise":
            with pytest.raises(expected_raise_type):
                stream.list_objects(params={}, account_id=account_id)
        elif expected_behavior == "remove_owner":
            stream.list_objects(params={}, account_id=account_id)
            # Verify api_get was called twice (first raises, second succeeds after removing "owner")
            assert mock_account_instance.api_get.call_count == 2
        elif expected_behavior == "remove_funding_source_details":
            stream.list_objects(params={}, account_id=account_id)
            assert mock_account_instance.api_get.call_count == 2


def _object_story_spec_read_error(subcode):
    """Build a Facebook 400 error body matching the Degrees-of-Freedom object_story_spec read failure."""
    return {
        "error": {
            "message": "Invalid parameter",
            "type": "OAuthException",
            "code": 100,
            "error_subcode": subcode,
            "is_transient": False,
            "error_user_title": "First Dof Value Should Match Object Story Spec Field",
            "error_user_msg": "For a Degrees of freedom enabled ad, the first value of Asset Feed Spec field "
            "should match the corresponding field in Object Story Spec.",
        }
    }


def _facebook_request_error(error_body, status_code=400):
    return FacebookRequestError(
        message=error_body["error"]["message"],
        request_context={},
        http_status=status_code,
        http_headers={},
        body=json.dumps(error_body),
    )


def _graph_next_url(url, after, fields):
    """Graph API `next` links repeat the whole request query, not only `after`."""
    query = {"access_token": "unknown_token", "fields": fields, "limit": 100, "summary": "true", "after": after}
    return f"{url}?{urlencode(query)}"


@pytest.mark.parametrize("error_subcode", [2446211, 1443048])
def test_fetch_creative_details_object_story_spec_fallback(api, some_config, error_subcode):
    """A creative whose stored object_story_spec fails validation is re-fetched without that field."""
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    expected_data = {"id": "12345", "name": "Test Creative"}
    exception = AirbyteTracedException(
        message="Facebook error", exception=_facebook_request_error(_object_story_spec_read_error(error_subcode))
    )

    with patch("source_facebook_marketing.streams.streams.FBAdCreative") as mock_creative_cls:
        mock_creative_instance = MagicMock()
        mock_creative_cls.return_value = mock_creative_instance
        mock_creative_instance.api_get.side_effect = [exception, mock_creative_instance]
        mock_creative_instance.export_all_data.return_value = expected_data

        result = stream._fetch_creative_details("12345")

    assert result == expected_data
    assert mock_creative_instance.api_get.call_count == 2
    first_fields = mock_creative_instance.api_get.call_args_list[0].kwargs["fields"]
    second_fields = mock_creative_instance.api_get.call_args_list[1].kwargs["fields"]
    assert "object_story_spec" in first_fields
    assert "object_story_spec" not in second_fields


def test_fetch_creative_details_unrelated_400_does_not_fallback(api, some_config):
    """A 400 with a different error_subcode still propagates and api_get is called only once."""
    stream = AdCreativesFromAds(api=api, account_ids=some_config["account_ids"], start_date=None, end_date=None)
    exception = AirbyteTracedException(message="Facebook error", exception=_facebook_request_error(_object_story_spec_read_error(33)))

    with patch("source_facebook_marketing.streams.streams.FBAdCreative") as mock_creative_cls:
        mock_creative_instance = MagicMock()
        mock_creative_cls.return_value = mock_creative_instance
        mock_creative_instance.api_get.side_effect = exception

        with pytest.raises(AirbyteTracedException):
            stream._fetch_creative_details("12345")

    assert mock_creative_instance.api_get.call_count == 1


def test_ad_creatives_object_story_spec_failed_page_reread(api, some_config, requests_mock, account_id):
    """A page that fails on object_story_spec is re-read creative by creative without losing other records."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    fields_csv = ",".join(stream.fields())
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/"
    creatives_url = f"{base_url}act_{account_id}/adcreatives"

    page1 = {
        "json": {
            "data": [{"id": "c1"}, {"id": "c2"}],
            "paging": {"cursors": {"after": "A"}, "next": _graph_next_url(creatives_url, "A", fields_csv)},
        },
        "status_code": 200,
    }
    failed_page = {"json": _object_story_spec_read_error(2446211), "status_code": 400}
    id_page = {
        "json": {
            "data": [{"id": "c3"}, {"id": "c4"}],
            "paging": {"cursors": {"after": "B"}, "next": _graph_next_url(creatives_url, "B", "id")},
        },
        "status_code": 200,
    }
    page_after_b = {"json": {"data": [{"id": "c5"}]}, "status_code": 200}
    requests_mock.register_uri("GET", creatives_url, [page1, failed_page, id_page, page_after_b])

    requests_mock.register_uri("GET", f"{base_url}c3/", json={"id": "c3", "object_story_spec": {"link_data": {"link": "x"}}})
    requests_mock.register_uri(
        "GET",
        f"{base_url}c4/",
        [
            {"json": _object_story_spec_read_error(2446211), "status_code": 400},
            {"json": {"id": "c4", "name": "creative 4"}},
        ],
    )

    records = list(
        stream.read_records(
            sync_mode=SyncMode.full_refresh,
            stream_state={},
            stream_slice={"account_id": account_id},
        )
    )

    assert [r["id"] for r in records] == ["c1", "c2", "c3", "c4", "c5"]
    assert records[2]["object_story_spec"] == {"link_data": {"link": "x"}}
    assert "object_story_spec" not in records[3]

    edge_requests = [r for r in requests_mock.request_history if r.path.endswith("/adcreatives")]
    assert len(edge_requests) == 4
    assert edge_requests[0].qs["fields"] == [fields_csv]
    assert "after" not in edge_requests[0].qs
    assert edge_requests[0].qs["limit"] == ["100"]
    assert edge_requests[1].qs["after"] == ["a"]
    assert edge_requests[1].qs["fields"] == [fields_csv]
    assert edge_requests[2].qs["fields"] == ["id"]
    assert edge_requests[2].qs["after"] == ["a"]
    assert edge_requests[2].qs["limit"] == ["100"]
    assert edge_requests[3].qs["after"] == ["b"]
    assert edge_requests[3].qs["fields"] == [fields_csv]

    c4_requests = [r for r in requests_mock.request_history if r.path.endswith("/c4/")]
    assert len(c4_requests) == 2
    assert "object_story_spec" in c4_requests[0].qs["fields"][0]
    assert "object_story_spec" not in c4_requests[1].qs["fields"][0]


def test_ad_creatives_object_story_spec_last_page_fails(api, some_config, requests_mock, account_id):
    """When the last page fails, the id page keeps the failed page's `after` (no `next`), so the stream ends instead of re-reading it."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/"
    creatives_url = f"{base_url}act_{account_id}/adcreatives"

    page1 = {
        "json": {
            "data": [{"id": "c1"}],
            "paging": {"cursors": {"after": "A"}, "next": _graph_next_url(creatives_url, "A", ",".join(stream.fields()))},
        },
        "status_code": 200,
    }
    failed_page = {"json": _object_story_spec_read_error(2446211), "status_code": 400}
    # Facebook keeps cursors.after on the last page and only omits "next".
    id_page = {"json": {"data": [{"id": "c2"}], "paging": {"cursors": {"after": "Z"}}}, "status_code": 200}
    requests_mock.register_uri("GET", creatives_url, [page1, failed_page, id_page, failed_page])
    requests_mock.register_uri("GET", f"{base_url}c2/", json={"id": "c2"})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.full_refresh,
            stream_state={},
            stream_slice={"account_id": account_id},
        )
    )

    assert [r["id"] for r in records] == ["c1", "c2"]
    edge_requests = [r for r in requests_mock.request_history if r.path.endswith("/adcreatives")]
    assert len(edge_requests) == 3
    assert edge_requests[2].qs["fields"] == ["id"]
    assert edge_requests[2].qs["after"] == ["a"]


def test_ad_creatives_object_story_spec_first_page_fails_no_next(api, some_config, requests_mock, account_id):
    """When the very first page fails and the id page has no next, creatives are emitted and the stream ends."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/"
    creatives_url = f"{base_url}act_{account_id}/adcreatives"

    failed_page = {"json": _object_story_spec_read_error(2446211), "status_code": 400}
    id_page = {"json": {"data": [{"id": "c1"}, {"id": "c2"}]}, "status_code": 200}
    requests_mock.register_uri("GET", creatives_url, [failed_page, id_page])
    requests_mock.register_uri("GET", f"{base_url}c1/", json={"id": "c1"})
    requests_mock.register_uri("GET", f"{base_url}c2/", json={"id": "c2"})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.full_refresh,
            stream_state={},
            stream_slice={"account_id": account_id},
        )
    )

    assert [r["id"] for r in records] == ["c1", "c2"]


def test_ad_creatives_pages_keep_cursor_patch_guards(api, some_config, requests_mock, account_id):
    """ad_creatives pages are read through CursorPatch, so a malformed item in `data` is dropped instead of crashing the read."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    creatives_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/act_{account_id}/adcreatives"
    requests_mock.register_uri("GET", creatives_url, json={"data": ["unexpected", {"id": "c1"}]})

    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}, stream_slice={"account_id": account_id}))

    assert [r["id"] for r in records] == ["c1"]


def test_ad_creatives_empty_first_page_keeps_paging(api, some_config, requests_mock, account_id):
    """Like get_ad_creatives(), an empty first page that still has a `next` link does not end the read."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    creatives_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/act_{account_id}/adcreatives"
    empty_page = {
        "json": {"data": [], "paging": {"cursors": {"after": "A"}, "next": _graph_next_url(creatives_url, "A", ",".join(stream.fields()))}},
        "status_code": 200,
    }
    requests_mock.register_uri("GET", creatives_url, [empty_page, {"json": {"data": [{"id": "c1"}]}, "status_code": 200}])

    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}, stream_slice={"account_id": account_id}))

    assert [r["id"] for r in records] == ["c1"]


@pytest.mark.parametrize(
    "error_subcode, deselect_object_story_spec",
    [(33, False), (2446211, True)],
    ids=["unrelated_error", "object_story_spec_not_requested"],
)
def test_ad_creatives_page_error_without_reread(api, some_config, requests_mock, account_id, error_subcode, deselect_object_story_spec):
    """A page error that dropping object_story_spec cannot fix fails the read as before, without re-reading the page."""
    stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
    if deselect_object_story_spec:
        stream.configured_json_schema = {"properties": {"id": {"type": ["null", "string"]}, "name": {"type": ["null", "string"]}}}
    creatives_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/act_{account_id}/adcreatives"
    requests_mock.register_uri("GET", creatives_url, json=_object_story_spec_read_error(error_subcode), status_code=400)

    with pytest.raises(AirbyteTracedException):
        list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}, stream_slice={"account_id": account_id}))

    assert len([r for r in requests_mock.request_history if r.path.endswith("/adcreatives")]) == 1
