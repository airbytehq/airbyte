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
_STREAM_NAME = "ad_creative_analytics"


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


def _create_creative_record(
    creative_id: int,
    account_id: int,
    name: str = "Test Creative",
    status: str = "ACTIVE",
    last_modified: str = "2024-06-01T00:00:00.000Z",
) -> dict:
    # The id must be a string URN format because the manifest uses .split(':')[-1] to extract the numeric ID
    return {
        "id": f"urn:li:sponsoredCreative:{creative_id}",
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "name": name,
        "status": status,
        "type": "TEXT_AD",
        "campaign": f"urn:li:sponsoredCampaign:{creative_id}",
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": last_modified,
        "version": {"versionTag": "1"},
    }


def _create_analytics_record(
    creative_id: int,
    end_date: str = "2024-06-01",
    impressions: int = 1000,
    clicks: int = 50,
) -> dict:
    return {
        "dateRange": {
            "start": {"year": 2024, "month": 6, "day": 1},
            "end": {"year": 2024, "month": 6, "day": 1},
        },
        "pivotValues": [f"urn:li:sponsoredCreative:{creative_id}"],
        "impressions": impressions,
        "clicks": clicks,
        "costInLocalCurrency": "10.00",
        "costInUsd": "10.00",
        "end_date": end_date,
        "string_of_pivot_values": f"urn:li:sponsoredCreative:{creative_id}",
    }


@freezegun.freeze_time("2024-06-15T00:00:00Z")
class TestAdCreativeAnalyticsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'ad_creative_analytics' stream.

    This is a substream of creatives that uses:
    - NoPagination (analytics endpoints don't paginate)
    - DatetimeBasedCursor with 30-day steps
    - Transformations that add 'sponsoredCreative' and 'pivot' fields
    - SubstreamPartitionRouter to iterate over parent creatives
    """

    @HttpMocker()
    def test_full_refresh_with_single_parent_creative(self, http_mocker: HttpMocker):
        """
        Test that connector fetches analytics for a parent creative.

        Given: A parent creative with analytics data
        When: Running a full refresh sync
        Then: The connector should fetch analytics for the creative
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "Creative 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(2001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["string_of_pivot_values"] == "urn:li:sponsoredCreative:2001"
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_transformations_applied(self, http_mocker: HttpMocker):
        """
        Test that transformations add 'sponsoredCreative' and 'pivot' fields.

        Given: Analytics data from the API
        When: Running a full refresh sync
        Then: Records should have 'sponsoredCreative' and 'pivot' fields added
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "Creative 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(2001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record_data = output.records[0].record.data

        assert "sponsoredCreative" in record_data
        assert record_data["sponsoredCreative"] == "2001"
        assert "pivot" in record_data
        assert record_data["pivot"] == "CREATIVE"

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Test incremental sync without prior state (first sync).

        Given: No prior state
        When: Running an incremental sync
        Then: All records should be returned and state should be emitted
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "Creative 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(2001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent stream gracefully.

        Given: No parent creatives
        When: Running a full refresh sync
        Then: No child requests should be made and zero records returned
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_parent_with_no_analytics_data(self, http_mocker: HttpMocker):
        """
        Test that connector handles parent with no analytics data gracefully.

        Given: A parent creative with no analytics data
        When: Running a full refresh sync
        Then: Zero records should be returned without errors
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "Creative 1")]),
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
        """
        Test that analytics records contain expected metric fields.

        Given: Analytics data with impressions and clicks
        When: Running a full refresh sync
        Then: Records should contain the expected metric fields
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "Creative 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(2001, "2024-06-01", 5000, 250)]).build(),
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
