#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import patch

import pytest
import source_bing_ads
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from source_bing_ads.reports import ReportsMixin
from source_bing_ads.source import SourceBingAds
from source_bing_ads.streams import AccountPerformanceReportMonthly, Accounts, AdGroups, Ads, AppInstallAds, BingAdsStream, Campaigns
from suds import TypeNotFound, WebFault
from unittest.mock import MagicMock
from bingads.service_info import SERVICE_INFO_DICT_V13

@pytest.fixture(name="config")
def config_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
    }


@pytest.fixture(name="config_with_custom_reports")
def config_with_custom_reports_fixture():
    """Generates streams settings with custom reports from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
        "custom_reports": [
            {
                "name": "my test custom report",
                "reporting_object": "DSAAutoTargetPerformanceReport",
                "report_columns": [
                    "AbsoluteTopImpressionRatePercent",
                    "AccountId",
                    "AccountName",
                    "AccountNumber",
                    "AccountStatus",
                    "AdDistribution",
                    "AdGroupId",
                    "AdGroupName",
                    "AdGroupStatus",
                    "AdId",
                    "AllConversionRate",
                    "AllConversions",
                    "AllConversionsQualified",
                    "AllCostPerConversion",
                    "AllReturnOnAdSpend",
                    "AllRevenue",
                ],
                "report_aggregation": "Weekly",
            }
        ],
    }


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_bing_ads.source.AirbyteLogger")


@patch.object(source_bing_ads.source, "Client")
def test_streams_config_based(mocked_client, config):
    streams = SourceBingAds().streams(config)
    assert len(streams) == 60


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
def test_validate_custom_reposts_failed_invalid_report_object(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    config_with_custom_reports["custom_reports"][0]["reporting_object"] = "NonExistingReportRequest"

    with pytest.raises(AirbyteTracedException) as e:
        SourceBingAds().validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
    assert e.value.internal_message == ("my test custom report: NonExistingReport: Reporting Data Object that"
                                        " you provided doesn't exist. Please ensure it is correct in Bing Ads Docs.")
    assert (
        "Config validation error: my test custom report: NonExistingReport: "
        "Reporting Data Object that you provided doesn't exist. Please ensure it is correct in Bing Ads Docs."
    ) in e.value.message


@patch.object(source_bing_ads.source, "Client")
def test_validate_custom_reposts_failed_invalid_report_columns(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    config_with_custom_reports["custom_reports"][0]["report_columns"] = ["TimePeriod", "NonExistingColumn", "ConversionRate"]

    with pytest.raises(AirbyteTracedException) as e:
        SourceBingAds().validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
    assert e.value.internal_message == ("my test custom report: Reporting Columns are invalid. "
                                        "Columns that you provided don't belong to Reporting Data Object Columns:"
                                        " ['TimePeriod', 'NonExistingColumn', 'ConversionRate']. "
                                        "Please ensure it is correct in Bing Ads Docs.")
    assert ('Config validation error: my test custom report: Reporting Columns are '
            "invalid. Columns that you provided don't belong to Reporting Data Object "
            "Columns: ['TimePeriod', 'NonExistingColumn', 'ConversionRate']. Please "
            'ensure it is correct in Bing Ads Docs.') in e.value.message


@patch.object(source_bing_ads.source, "Client")
def test_get_custom_reports(mocked_client, config_with_custom_reports):
    custom_reports = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)
    assert isinstance(custom_reports, list)
    assert custom_reports[0].report_name == "DSAAutoTargetPerformanceReport"
    assert custom_reports[0].report_aggregation == "Weekly"
    assert "AccountId" in custom_reports[0].custom_report_columns


def test_validate_reporting_object_name():
    reporting_object = SourceBingAds()._validate_reporting_object_name("DSAAutoTargetPerformanceReportRequest")
    assert reporting_object == "DSAAutoTargetPerformanceReport"
    reporting_object = SourceBingAds()._validate_reporting_object_name("DSAAutoTargetPerformanceReport")
    assert reporting_object == "DSAAutoTargetPerformanceReport"


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
    request_params = accountperformancereportmonthly.request_params(account_id=180278106, stream_slice={"time_period": "ThisYear"})
    del request_params["report_request"]
    assert request_params == {
        "overwrite_result_file": True,
        # 'report_request': <MagicMock name='Client.get_service().factory.create()' id='140040029053232'>,
        "result_file_directory": "/tmp",
        "result_file_name": "AccountPerformanceReport",
        "timeout_in_milliseconds": 300000,
    }


@patch.object(source_bing_ads.source, "Client")
def test_AccountPerformanceReportMonthly_stream_slices(mocked_client, config):

    accountperformancereportmonthly = AccountPerformanceReportMonthly(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        stream_slice = list(accountperformancereportmonthly.stream_slices())
        assert stream_slice == [
            {"account_id": 180519267, "customer_id": 100, "time_period": "LastYear"},
            {"account_id": 180519267, "customer_id": 100, "time_period": "ThisYear"},
            {"account_id": 180278106, "customer_id": 200, "time_period": "LastYear"},
            {"account_id": 180278106, "customer_id": 200, "time_period": "ThisYear"},
        ]


@pytest.mark.parametrize(
    ("stream", "stream_slice"),
    (
        (Accounts, {}),
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
def test_bulk_stream_stream_slices(mocked_client, config):
    slices = AppInstallAds(mocked_client, config).stream_slices()
    assert list(slices) == []

    app_install_ads = AppInstallAds(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        slices = app_install_ads.stream_slices()
        assert list(slices) == [{"account_id": 180519267, "customer_id": 100}, {"account_id": 180278106, "customer_id": 200}]


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_transfrom(mocked_client, config):
    record = {"Ad Group": "Ad Group", "App Id": "App Id", "Campaign": "Campaign", "Custom Parameter": "Custom Parameter"}
    transformed_record = AppInstallAds(mocked_client, config).transform(
        record=record, stream_slice={"account_id": 180519267, "customer_id": 100}
    )
    assert transformed_record == {
        "Account Id": 180519267,
        "Ad Group": "Ad Group",
        "App Id": "App Id",
        "Campaign": "Campaign",
        "Custom Parameter": "Custom Parameter",
    }


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_read_with_chunks(mocked_client, config):
    path_to_file = Path(__file__).parent / "app_install_ads.csv"
    path_to_file_base = Path(__file__).parent / "app_install_ads_base.csv"
    with open(path_to_file_base, "r") as f1, open(path_to_file, "a") as f2:
        for line in f1:
            f2.write(line)

    app_install_ads = AppInstallAds(mocked_client, config)
    result = app_install_ads.read_with_chunks(path=path_to_file)
    assert next(result) == {
        "Ad Group": "AdGroupNameGoesHere",
        "App Id": "AppStoreIdGoesHere",
        "App Platform": "Android",
        "Campaign": "ParentCampaignNameGoesHere",
        "Client Id": "ClientIdGoesHere",
        "Custom Parameter": "{_promoCode}=PROMO1; {_season}=summer",
        "Destination Url": None,
        "Device Preference": "All",
        "Display Url": None,
        "Final Url": "FinalUrlGoesHere",
        "Final Url Suffix": None,
        "Id": None,
        "Mobile Final Url": None,
        "Modified Time": None,
        "Name": None,
        "Parent Id": "-1111",
        "Promotion": None,
        "Status": "Active",
        "Text": "Find New Customers & Increase Sales!",
        "Title": "Contoso Quick Setup",
        "Tracking Template": None,
        "Type": "App Install Ad",
    }


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
