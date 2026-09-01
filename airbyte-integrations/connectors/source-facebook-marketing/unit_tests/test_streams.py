#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from facebook_business.exceptions import FacebookRequestError
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
