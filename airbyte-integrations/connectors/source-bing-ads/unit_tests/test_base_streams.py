#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import find_stream, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": {"KeyValuePairOfstringbase64Binary": [{"key": "test key", "value": "test value"}]},
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01",
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01",
            },
        ),
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01",
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01",
            },
        ),
        (
            {"AccountId": 16253412, "LastModifiedTime": "2025-01-01"},
            {"AccountId": 16253412, "LastModifiedTime": "2025-01-01"},
        ),
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": None,
                "LastModifiedTime": "2025-01-01",
            },
            {"AccountId": 16253412, "TaxCertificate": None, "LastModifiedTime": "2025-01-01"},
        ),
    ],
    ids=[
        "record_with_KeyValuePairOfstringbase64Binary_field",
        "record_without_KeyValuePairOfstringbase64Binary_field",
        "record_without_TaxCertificate_field",
        "record_with_TaxCertificate_is_None",
    ],
)
def test_accounts_transform_tax_fields(config, record, expected):
    stream = find_stream("accounts", config)
    transformed_record = list(
        stream.retriever.record_selector.filter_and_transform(all_data=[record], stream_state={}, stream_slice={}, records_schema={})
    )[0]
    if expected.get("TaxCertificate"):
        assert transformed_record["TaxCertificate"] == expected["TaxCertificate"]
    else:
        assert expected.get("TaxCertificate") is None
        assert transformed_record.get("TaxCertificate") is None


def test_campaigns_request_params(config):
    campaigns = find_stream("campaigns", config)
    stream_slice = StreamSlice(partition={"account_id": "account_id"}, cursor_slice={})
    request_params = campaigns.retriever.requester.get_request_body_json(stream_slice=stream_slice)
    assert request_params
    assert request_params["AccountId"] == "account_id"
    assert request_params["CampaignType"] == "Audience,DynamicSearchAds,Search,Shopping,PerformanceMax"
    assert (
        request_params["ReturnAdditionalFields"]
        == "AdScheduleUseSearcherTimeZone,BidStrategyId,CpvCpmBiddingScheme,DynamicDescriptionSetting,DynamicFeedSetting,MaxConversionValueBiddingScheme,MultimediaAdsBidAdjustment,TargetImpressionShareBiddingScheme,TargetSetting,VerifiedTrackingSetting"
    )


def test_campaigns_stream_slices(config, logger_mock, mock_auth_token, mock_user_query, mock_account_query):
    campaigns = find_stream("campaigns", config)
    slices = campaigns.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={})
    assert list(slices) == [
        {"account_id": 1, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}},
        {"account_id": 2, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}},
        {"account_id": 3, "parent_slice": {"account_name": "", "user_id": 1, "parent_slice": {}}},
    ]


def test_adgroups_stream_slices(mock_auth_token, mock_user_query, mock_account_query, requests_mock, config):
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


def test_ads_stream_slices(mock_auth_token, mock_user_query, mock_account_query, requests_mock, config):
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
    "stream",
    (
        "accounts",
        "ad_groups",
        "ads",
        "campaigns",
    ),
)
def test_streams_full_refresh(config, stream, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    requests_mock.post(
        "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/Campaigns/QueryByAccountId",
        status_code=200,
        json={
            "Campaigns": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
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
    requests_mock.post(
        "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/Ads/QueryByAdGroupId",
        status_code=200,
        json={
            "Ads": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )

    state = StateBuilder().with_stream_state(stream, {}).build()
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    source = get_source(config, state)
    output = read(source, config, catalog, state)
    assert len(output.records) == 3


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
