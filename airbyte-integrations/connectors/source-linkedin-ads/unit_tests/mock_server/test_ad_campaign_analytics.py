# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

import freezegun
import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import ExpectedOutcome, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import (
    LinkedInAdsAnalyticsResponseBuilder,
    LinkedInAdsPaginatedResponseBuilder,
)


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "ad_campaign_analytics"
_PARENT_STREAM_NAME = "campaigns"
_GRANDPARENT_STREAM_NAME = "accounts"
_DATA_VOLUME_RATE_LIMIT_MESSAGE = (
    "The data request limit has been exceeded. More than 45 million metric values were requested in a 5-minute window."
)


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
        "costType": "CPM",
        "dailyBudget": {"amount": "100.00", "currencyCode": "USD"},
        "totalBudget": {"amount": "1000.00", "currencyCode": "USD"},
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
    """
    Create an analytics record.

    Note: The 'sponsoredCampaign' and 'pivot' fields are added by transformations
    in the manifest, so they should appear in the output records.
    """
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
class TestAdCampaignAnalyticsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'ad_campaign_analytics' stream.

    This is a substream of campaigns that uses:
    - NoPagination (analytics endpoints don't paginate)
    - DatetimeBasedCursor with 30-day steps
    - Transformations that add 'sponsoredCampaign' and 'pivot' fields
    - CustomRecordExtractor and CustomErrorHandler
    - SubstreamPartitionRouter to iterate over parent campaigns
    """

    @HttpMocker()
    def test_full_refresh_with_single_parent_campaign(self, http_mocker: HttpMocker):
        """
        Test that connector fetches analytics for a parent campaign.

        Given: A parent campaign with analytics data
        When: Running a full refresh sync
        Then: The connector should fetch analytics for the campaign
        """
        config = ConfigBuilder().with_start_date("2024-06-01").build()

        # Mock accounts endpoint (grandparent)
        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        # Mock campaigns endpoint (parent)
        http_mocker.get(
            LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111, "Campaign 1")]),
        )

        # Mock analytics endpoint
        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_analytics_record(1001, "2024-06-01", 1000, 50)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        # Verify record has the expected campaign ID in pivot values
        assert output.records[0].record.data["string_of_pivot_values"] == "urn:li:sponsoredCampaign:1001"
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_transformations_applied(self, http_mocker: HttpMocker):
        """
        Test that transformations add 'sponsoredCampaign' and 'pivot' fields.

        Given: Analytics data from the API
        When: Running a full refresh sync
        Then: Records should have 'sponsoredCampaign' and 'pivot' fields added
        """
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

        # Verify transformations added the expected fields
        assert "sponsoredCampaign" in record_data
        assert record_data["sponsoredCampaign"] == "1001"
        assert "pivot" in record_data
        assert record_data["pivot"] == "CAMPAIGN"

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
        """
        Test that connector handles empty parent stream gracefully.

        Given: No parent campaigns
        When: Running a full refresh sync
        Then: No child requests should be made and zero records returned
        """
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
        """
        Test that connector handles parent with no analytics data gracefully.

        Given: A parent campaign with no analytics data
        When: Running a full refresh sync
        Then: Zero records should be returned without errors
        """
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

        # Verify analytics metrics are present
        assert record_data["impressions"] == 5000
        assert record_data["clicks"] == 250
        # Note: dateRange is processed by the custom record extractor and converted to end_date/start_date
        assert "end_date" in record_data
        assert "start_date" in record_data


def _configure_rate_limit_test_parents(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
        LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111)]),
    )
    http_mocker.get(
        LinkedInAdsRequestBuilder.campaigns_endpoint(111111111).with_any_query_params().build(),
        LinkedInAdsPaginatedResponseBuilder.single_page([_create_campaign_record(1001, 111111111)]),
    )


def _read_campaign_analytics(config: dict, expected_outcome: ExpectedOutcome = ExpectedOutcome.EXPECT_SUCCESS):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(source, config=config, catalog=catalog, expected_outcome=expected_outcome)


@freezegun.freeze_time("2024-06-15T00:00:00Z")
def test_data_volume_rate_limit_retry() -> None:
    config = ConfigBuilder().with_start_date("2024-06-01").build()
    sleeps = []

    with HttpMocker() as http_mocker, patch("time.sleep", side_effect=lambda seconds: sleeps.append(float(seconds))):
        _configure_rate_limit_test_parents(http_mocker)
        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            [
                HttpResponse(status_code=429, body=json.dumps({"message": _DATA_VOLUME_RATE_LIMIT_MESSAGE})),
                LinkedInAdsAnalyticsResponseBuilder.single_page([_create_analytics_record(1001)]),
            ],
        )

        output = _read_campaign_analytics(config)

        assert len(output.records) == 1
        assert output.records[0].record.stream == _STREAM_NAME
        assert [seconds for seconds in sleeps if seconds > 0] == [331.0]
        assert output.errors == []


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(json.dumps({"message": "Rate limit exceeded."}), id="generic_json"),
        pytest.param("not-json", id="malformed_body"),
    ],
)
@freezegun.freeze_time("2024-06-15T00:00:00Z")
def test_non_data_volume_rate_limit_fallback(body: str) -> None:
    config = ConfigBuilder().with_start_date("2024-06-01").build()
    sleeps = []

    with HttpMocker() as http_mocker, patch("time.sleep", side_effect=lambda seconds: sleeps.append(float(seconds))):
        _configure_rate_limit_test_parents(http_mocker)
        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            [
                HttpResponse(status_code=429, body=body),
                LinkedInAdsAnalyticsResponseBuilder.single_page([_create_analytics_record(1001)]),
            ],
        )

        output = _read_campaign_analytics(config)

        assert len(output.records) == 1
        assert [seconds for seconds in sleeps if seconds > 0] == [11.0]
        assert output.errors == []


@freezegun.freeze_time("2024-06-15T00:00:00Z")
def test_uri_too_long_failure() -> None:
    config = ConfigBuilder().with_start_date("2024-06-01").build()
    sleeps = []

    with HttpMocker() as http_mocker, patch("time.sleep", side_effect=lambda seconds: sleeps.append(float(seconds))):
        _configure_rate_limit_test_parents(http_mocker)
        http_mocker.get(
            LinkedInAdsRequestBuilder.ad_analytics_endpoint().with_any_query_params().build(),
            HttpResponse(status_code=414, body="{}"),
        )

        output = _read_campaign_analytics(config, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        errors = [message.trace.error for message in output.errors if message.trace.error.failure_type == FailureType.system_error]
        assert output.records == []
        assert len(errors) == 1
        assert errors[0].message == "LinkedIn Ads request URL exceeds the API length limit."
        assert [seconds for seconds in sleeps if seconds > 0] == []
