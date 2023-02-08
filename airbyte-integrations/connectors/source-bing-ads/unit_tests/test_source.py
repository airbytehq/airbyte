#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

import pytest
import source_bing_ads
from airbyte_cdk.models import SyncMode
from source_bing_ads.source import AccountPerformanceReportMonthly, Accounts, AdGroups, Ads, Campaigns, SourceBingAds


@pytest.fixture(name="config")
def config_fixture():
    """Generates streams settings from a config file"""
    CONFIG_FILE = "secrets/config.json"
    with open(CONFIG_FILE, "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_bing_ads.source.AirbyteLogger")


@patch.object(source_bing_ads.source, "Client")
def test_streams_config_based(mocked_client, config):
    streams = SourceBingAds().streams(config)
    assert len(streams) == 25


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_ok(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=iter([{"Id": 180519267}, {"Id": 180278106}])):
        assert SourceBingAds().check_connection(logger_mock, config=config) == (True, None)


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_failed(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=0):
        assert SourceBingAds().check_connection(logger_mock, config=config)[0] is False


@patch.object(source_bing_ads.source, "Client")
def test_campaigns_request_params(mocked_client, config):

    campaigns = Campaigns(mocked_client, config)

    request_params = campaigns.request_params(stream_slice={"account_id": "account_id"})
    assert request_params == {
        "AccountId": "account_id",
        "CampaignType": "Audience DynamicSearchAds Search Shopping",
        "ReturnAdditionalFields": "AdScheduleUseSearcherTimeZone BidStrategyId CpvCpmBiddingScheme DynamicDescriptionSetting DynamicFeedSetting MaxConversionValueBiddingScheme MultimediaAdsBidAdjustment TargetImpressionShareBiddingScheme TargetSetting VerifiedTrackingSetting",
    }


@patch.object(source_bing_ads.source, "Client")
def test_campaigns_stream_slices(mocked_client, config):

    campaigns = Campaigns(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        slices = campaigns.stream_slices()
        assert list(slices) == [
            {"account_id": 180519267, "customer_id": 100},
            {"account_id": 180278106, "customer_id": 200},
        ]


@patch.object(source_bing_ads.source, "Client")
def test_adgroups_stream_slices(mocked_client, config):

    adgroups = AdGroups(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    campaigns_read_records = [iter([{"Id": 11}, {"Id": 22}]), iter([{"Id": 55}, {"Id": 66}])]
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        with patch.object(Campaigns, "read_records", side_effect=campaigns_read_records):
            slices = adgroups.stream_slices()
            assert list(slices) == [
                {"campaign_id": 11, "account_id": 180519267, "customer_id": 100},
                {"campaign_id": 22, "account_id": 180519267, "customer_id": 100},
                {"campaign_id": 55, "account_id": 180278106, "customer_id": 200},
                {"campaign_id": 66, "account_id": 180278106, "customer_id": 200},
            ]


@patch.object(source_bing_ads.source, "Client")
def test_ads_request_params(mocked_client, config):

    ads = Ads(mocked_client, config)

    request_params = ads.request_params(stream_slice={"ad_group_id": "ad_group_id"})
    assert request_params == {
        "AdGroupId": "ad_group_id",
        "AdTypes": {
            "AdType": ["Text", "Image", "Product", "AppInstall", "ExpandedText", "DynamicSearch", "ResponsiveAd", "ResponsiveSearch"]
        },
        "ReturnAdditionalFields": "ImpressionTrackingUrls Videos LongHeadlines",
    }


@patch.object(source_bing_ads.source, "Client")
def test_ads_stream_slices(mocked_client, config):

    ads = Ads(mocked_client, config)

    with patch.object(
        AdGroups,
        "stream_slices",
        return_value=iter([{"account_id": 180519267, "customer_id": 100}, {"account_id": 180278106, "customer_id": 200}]),
    ):
        with patch.object(AdGroups, "read_records", side_effect=[iter([{"Id": 11}, {"Id": 22}]), iter([{"Id": 55}, {"Id": 66}])]):
            slices = ads.stream_slices()
            assert list(slices) == [
                {"ad_group_id": 11, "account_id": 180519267, "customer_id": 100},
                {"ad_group_id": 22, "account_id": 180519267, "customer_id": 100},
                {"ad_group_id": 55, "account_id": 180278106, "customer_id": 200},
                {"ad_group_id": 66, "account_id": 180278106, "customer_id": 200},
            ]


@patch.object(source_bing_ads.source, "Client")
def test_AccountPerformanceReportMonthly_request_params(mocked_client, config):

    accountperformancereportmonthly = AccountPerformanceReportMonthly(mocked_client, config)
    request_params = accountperformancereportmonthly.request_params(account_id=180278106)
    del request_params["report_request"]
    assert request_params == {
        "overwrite_result_file": True,
        # 'report_request': <MagicMock name='Client.get_service().factory.create()' id='140040029053232'>,
        "result_file_directory": "/tmp",
        "result_file_name": "AccountPerformanceReport",
        "timeout_in_milliseconds": 300000,
    }


@patch.object(source_bing_ads.source, "Client")
def test_accounts(mocked_client, config):
    accounts = Accounts(mocked_client, config)
    _ = list(accounts.read_records(SyncMode.full_refresh))
    mocked_client.request.assert_called_once()
