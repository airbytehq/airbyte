# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import (
    LinkedInAdsAnalyticsResponseBuilder,
    LinkedInAdsPaginatedResponseBuilder,
)


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "ad_member_country_analytics"
_PIVOT_VALUE = "MEMBER_COUNTRY_V2"


def _create_account_record(account_id: int, name: str = "Test Account") -> dict:
    return {
        "id": account_id,
        "name": name,
        "type": "BUSINESS",
        "status": "ACTIVE",
        "currency": "USD",
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": "2024-06-01T00:00:00.000Z",
    }


def _create_campaign_record(
    campaign_id: int,
    account_id: int,
    name: str = "Test Campaign",
    status: str = "ACTIVE",
    last_modified: str = "2024-06-01T00:00:00.000Z",
) -> dict:
    return {
        "id": campaign_id,
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "name": name,
        "status": status,
        "type": "TEXT_AD",
        "campaignGroup": f"urn:li:sponsoredCampaignGroup:{campaign_id}",
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": last_modified,
        "version": {"versionTag": "1"},
    }


def _create_analytics_record(
    campaign_id: int,
    end_date: str = "2024-06-01",
    impressions: int = 1000,
    clicks: int = 50,
) -> dict:
    return {
        "dateRange": {
            "start": {"year": 2024, "month": 6, "day": 1},
            "end": {"year": 2024, "month": 6, "day": 1},
        },
        "pivotValues": [f"urn:li:sponsoredCampaign:{campaign_id}"],
        "impressions": impressions,
        "clicks": clicks,
        "costInLocalCurrency": "10.00",
        "costInUsd": "10.00",
        "end_date": end_date,
        "string_of_pivot_values": f"urn:li:sponsoredCampaign:{campaign_id}",
    }


@freezegun.freeze_time("2024-06-15T00:00:00Z")
class TestAdMemberCountryAnalyticsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'ad_member_country_analytics' stream.

    This is a substream of campaigns that uses:
    - NoPagination (analytics endpoints don't paginate)
    - DatetimeBasedCursor with 30-day steps
    - Transformations that add 'sponsoredCampaign' and 'pivot' fields
    - SubstreamPartitionRouter to iterate over parent campaigns

    Note: This stream follows the same pattern as ad_campaign_analytics but with
    pivot value MEMBER_COUNTRY_V2 instead of CAMPAIGN.
    """

    @HttpMocker()
    def test_full_refresh_with_single_parent_campaign(self, http_mocker: HttpMocker):
        """Test that connector fetches analytics for a parent campaign."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(1001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_transformations_applied(self, http_mocker: HttpMocker):
        """Test that transformations add 'sponsoredCampaign' and 'pivot' fields."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(1001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record_data = output.records[0].record.data

        assert "sponsoredCampaign" in record_data
        assert record_data["sponsoredCampaign"] == "1001"
        assert "pivot" in record_data
        assert record_data["pivot"] == _PIVOT_VALUE

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """Test incremental sync without prior state (first sync)."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(1001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """Test that connector handles empty parent stream gracefully."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_parent_with_no_analytics_data(self, http_mocker: HttpMocker):
        """Test that connector handles parent with no analytics data gracefully."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder.empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_analytics_data_fields(self, http_mocker: HttpMocker):
        """Test that analytics records contain expected metric fields."""
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(1001, "2024-06-01", 5000, 250)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record_data = output.records[0].record.data

        assert record_data["impressions"] == 5000
        assert record_data["clicks"] == 250
        assert "end_date" in record_data
        assert "start_date" in record_data
