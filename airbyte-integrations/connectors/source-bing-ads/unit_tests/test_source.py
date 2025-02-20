#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import source_bing_ads
from bingads.service_info import SERVICE_INFO_DICT_V13
from source_bing_ads.base_streams import Accounts, AdGroups, Ads, Campaigns
from source_bing_ads.source import SourceBingAds

from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException


@patch.object(source_bing_ads.source, "Client")
def test_streams_config_based(mocked_client, config):
    streams = SourceBingAds().streams(config)
    assert len(streams) == 77


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_ok(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=iter([{"Id": 180519267}, {"Id": 180278106}])):
        assert SourceBingAds().check_connection(logger_mock, config=config) == (True, None)


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_failed_user_do_not_have_accounts(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=[]):
        connected, reason = SourceBingAds().check_connection(logger_mock, config=config)
        assert connected is False
        assert (
            reason.message == "Config validation error: You don't have accounts assigned to this user. Please verify your developer token."
        )


def test_source_check_connection_failed_invalid_creds(config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=[]):
        connected, reason = SourceBingAds().check_connection(logger_mock, config=config)
        assert connected is False
        assert (
            reason.internal_message
            == "Failed to get OAuth access token by refresh token. The user could not be authenticated as the grant is expired. The user must sign in again."
        )


@patch.object(source_bing_ads.source, "Client")
def test_validate_custom_reposts(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    res = SourceBingAds().validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
    assert res is None


@patch.object(source_bing_ads.source, "Client")
def test_validate_custom_reposts_failed_invalid_report_columns(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    config_with_custom_reports["custom_reports"][0]["report_columns"] = ["TimePeriod", "NonExistingColumn", "ConversionRate"]

    with pytest.raises(AirbyteTracedException) as e:
        SourceBingAds().validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
    assert e.value.internal_message == (
        "my test custom report: Reporting Columns are invalid. "
        "Columns that you provided don't belong to Reporting Data Object Columns:"
        " ['TimePeriod', 'NonExistingColumn', 'ConversionRate']. "
        "Please ensure it is correct in Bing Ads Docs."
    )
    assert (
        "Config validation error: my test custom report: Reporting Columns are "
        "invalid. Columns that you provided don't belong to Reporting Data Object "
        "Columns: ['TimePeriod', 'NonExistingColumn', 'ConversionRate']. Please "
        "ensure it is correct in Bing Ads Docs."
    ) in e.value.message


@patch.object(source_bing_ads.source, "Client")
def test_get_custom_reports(mocked_client, config_with_custom_reports):
    custom_reports = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)
    assert isinstance(custom_reports, list)
    assert custom_reports[0].report_name == "DSAAutoTargetPerformanceReport"
    assert custom_reports[0].report_aggregation == "Weekly"
    assert "AccountId" in custom_reports[0].custom_report_columns


def test_clear_reporting_object_name():
    reporting_object = SourceBingAds()._clear_reporting_object_name("DSAAutoTargetPerformanceReportRequest")
    assert reporting_object == "DSAAutoTargetPerformanceReport"
    reporting_object = SourceBingAds()._clear_reporting_object_name("DSAAutoTargetPerformanceReport")
    assert reporting_object == "DSAAutoTargetPerformanceReport"


@patch.object(source_bing_ads.source, "Client")
def test_campaigns_request_params(mocked_client, config):
    campaigns = Campaigns(mocked_client, config)

    request_params = campaigns.request_params(stream_slice={"account_id": "account_id"})
    assert request_params == {
        "AccountId": "account_id",
        "CampaignType": "Audience DynamicSearchAds Search Shopping PerformanceMax",
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


@pytest.mark.parametrize(
    ("stream", "stream_slice"),
    (
        (
            Accounts,
            {
                "predicates": {
                    "Predicate": [
                        {"Field": "UserId", "Operator": "Equals", "Value": "131313131"},
                    ]
                }
            },
        ),
        (AdGroups, {"campaign_id": "campaign_id"}),
        (Ads, {"ad_group_id": "ad_group_id"}),
        (Campaigns, {"account_id": "account_id"}),
    ),
)
@patch.object(source_bing_ads.source, "Client")
def test_streams_full_refresh(mocked_client, config, stream, stream_slice):
    stream_instance = stream(mocked_client, config)
    _ = list(stream_instance.read_records(SyncMode.full_refresh, stream_slice))
    mocked_client.request.assert_called_once()


@patch.object(source_bing_ads.source, "Client")
def test_transform(mocked_client, config):
    record = {"AdFormatPreference": "All", "DevicePreference": 0, "EditorialStatus": "ActiveLimited", "FinalAppUrls": None}
    transformed_record = Ads(mocked_client, config).transform(
        record=record, stream_slice={"ad_group_id": 90909090, "account_id": 909090, "customer_id": 9090909}
    )
    assert transformed_record == {
        "AccountId": 909090,
        "AdFormatPreference": "All",
        "AdGroupId": 90909090,
        "CustomerId": 9090909,
        "DevicePreference": 0,
        "EditorialStatus": "ActiveLimited",
        "FinalAppUrls": None,
    }


@patch.object(source_bing_ads.source, "Client")
def test_check_connection_with_accounts_names_config(mocked_client, config_with_account_names, logger_mock):
    with patch.object(Accounts, "read_records", return_value=iter([{"Id": 180519267}, {"Id": 180278106}])):
        assert SourceBingAds().check_connection(logger_mock, config=config_with_account_names) == (True, None)
