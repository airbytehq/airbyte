#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import source_bing_ads
from bingads.service_info import SERVICE_INFO_DICT_V13
from conftest import find_stream
from helpers import source
from source_bing_ads.base_streams import Accounts, Campaigns

from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException


@patch.object(source_bing_ads.source, "Client")
def test_streams_config_based(mocked_client, config):
    streams = source(config).streams(config)
    assert len(streams) == 77


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_ok(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=iter([{"Id": 180519267}, {"Id": 180278106}])):
        assert source(config).check_connection(logger_mock, config=config) == (True, None)


@patch.object(source_bing_ads.source, "Client")
def test_source_check_connection_failed_user_do_not_have_accounts(mocked_client, config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=[]):
        connected, reason = source(config).check_connection(logger_mock, config=config)
        assert connected is False
        assert (
            reason.message == "Config validation error: You don't have accounts assigned to this user. Please verify your developer token."
        )


def test_source_check_connection_failed_invalid_creds(config, logger_mock):
    with patch.object(Accounts, "read_records", return_value=[]):
        connected, reason = source(config).check_connection(logger_mock, config=config)
        assert connected is False


@patch.object(source_bing_ads.source, "Client")
def test_validate_custom_reposts(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    res = source(config_with_custom_reports).validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
    assert res is None


@patch.object(source_bing_ads.source, "Client")
def test_validate_custom_reposts_failed_invalid_report_columns(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"
    config_with_custom_reports["custom_reports"][0]["report_columns"] = ["TimePeriod", "NonExistingColumn", "ConversionRate"]

    with pytest.raises(AirbyteTracedException) as e:
        source(config_with_custom_reports).validate_custom_reposts(config=config_with_custom_reports, client=mocked_client)
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
    custom_reports = source(config_with_custom_reports).get_custom_reports(config_with_custom_reports, mocked_client)
    assert isinstance(custom_reports, list)
    assert custom_reports[0].report_name == "DSAAutoTargetPerformanceReport"
    assert custom_reports[0].report_aggregation == "Weekly"
    assert "AccountId" in custom_reports[0].custom_report_columns


def test_clear_reporting_object_name():
    reporting_object = source(config={})._clear_reporting_object_name("DSAAutoTargetPerformanceReportRequest")
    assert reporting_object == "DSAAutoTargetPerformanceReport"
    reporting_object = source(config={})._clear_reporting_object_name("DSAAutoTargetPerformanceReport")
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


def test_adgroups_stream_slices(mock_auth_token, requests_mock, config):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query",
        status_code=200,
        json={"User": {"Id": 1}},
    )
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        status_code=200,
        json={
            "Accounts": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )
    requests_mock.post(
        "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/Campaigns/QueryByAccountId",
        status_code=200,
        json={
            "Campaigns": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )
    ad_groups = find_stream("ad_groups", config)
    stream_slices = list(ad_groups.retriever.stream_slicer.stream_slices())
    assert stream_slices == [
        {"campaign_id": [1], "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}]},
        {"campaign_id": [2], "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}]},
        {"campaign_id": [3], "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}]},
    ]


def test_ads_request_body_data(mock_auth_token, config):
    ads = find_stream("ads", config)
    stream_slice = {
        "campaign_id": [1],
        "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "AccountName", "user_id": 1, "parent_slice": {}}}],
    }

    request_params = ads.retriever.requester.get_request_body_json(stream_slice=stream_slice)
    assert request_params == {
        "AdTypes": ["Text", "Image", "Product", "AppInstall", "ExpandedText", "DynamicSearch", "ResponsiveAd", "ResponsiveSearch"],
        "ReturnAdditionalFields": "ImpressionTrackingUrls,Videos,LongHeadlines",
    }


def test_ads_stream_slices(mock_auth_token, requests_mock, config):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query",
        status_code=200,
        json={"User": {"Id": 1}},
    )
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        status_code=200,
        json={
            "Accounts": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )
    requests_mock.post(
        "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/Campaigns/QueryByAccountId",
        status_code=200,
        json={
            "Campaigns": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )
    requests_mock.post(
        "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/AdGroups/QueryByCampaignId",
        status_code=200,
        json={
            "AdGroups": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )
    ads = find_stream("ads", config)
    stream_slices = list(ads.retriever.stream_slicer.stream_slices())
    assert stream_slices == [
        {
            "ad_group_id": [1],
            "parent_slice": [
                {
                    "campaign_id": [1],
                    "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}],
                }
            ],
        },
        {
            "ad_group_id": [2],
            "parent_slice": [
                {
                    "campaign_id": [1],
                    "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}],
                }
            ],
        },
        {
            "ad_group_id": [3],
            "parent_slice": [
                {
                    "campaign_id": [1],
                    "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}],
                }
            ],
        },
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
        (Campaigns, {"account_id": "account_id"}),
    ),
)
@patch.object(source_bing_ads.source, "Client")
def test_streams_full_refresh(mocked_client, config, stream, stream_slice):
    stream_instance = stream(mocked_client, config)
    _ = list(stream_instance.read_records(SyncMode.full_refresh, stream_slice))
    mocked_client.request.assert_called_once()


def test_transform(mock_auth_token, config):
    record = {"AdFormatPreference": "All", "DevicePreference": 0, "EditorialStatus": "ActiveLimited", "FinalAppUrls": None}
    ads_stream = find_stream("ads", config)
    expected_record = {
        "AccountId": 909090,
        "AdFormatPreference": "All",
        "AdGroupId": 90909090,
        "CustomerId": 9090909,
        "Descriptions": None,
        "DevicePreference": 0,
        "EditorialStatus": "ActiveLimited",
        "FinalAppUrls": None,
        "FinalMobileUrls": None,
        "FinalUrls": None,
        "ForwardCompatibilityMap": None,
        "Headlines": None,
        "Images": None,
        "LongHeadlines": None,
        "Path1": None,
        "Path2": None,
        "TextPart2": None,
        "TitlePart3": None,
        "Videos": None,
    }
    transformed_record = list(
        ads_stream.retriever.record_selector.filter_and_transform(
            all_data=[
                record,
            ],
            stream_state=None,
            records_schema={},
            stream_slice={
                "ad_group_id": [90909090],
                "extra_fields": {"AccountId": [909090], "CustomerId": [9090909]},
                "parent_slice": [
                    {
                        "campaign_id": [1],
                        "parent_slice": [{"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}}],
                    }
                ],
            },
        )
    )[0]
    assert dict(sorted(transformed_record.items())) == dict(sorted(expected_record.items()))


@patch.object(source_bing_ads.source, "Client")
def test_check_connection_with_accounts_names_config(mocked_client, config_with_account_names, logger_mock):
    with patch.object(Accounts, "read_records", return_value=iter([{"Id": 180519267}, {"Id": 180278106}])):
        assert source(config=config_with_account_names).check_connection(logger_mock, config=config_with_account_names) == (True, None)
