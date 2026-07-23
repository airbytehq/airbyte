# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase
from urllib.parse import parse_qs, urlparse

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
_STREAM_NAME = "custom_statistics_report"
_PARENT_STREAM_NAME = "campaigns"
_GRANDPARENT_STREAM_NAME = "accounts"


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


def _create_statistics_record(
    campaign_id: int,
    creative_id: int,
    impressions: int = 1000,
    clicks: int = 50,
) -> dict:
    """
    Create a Statistics Finder record for custom_statistics_report.

    Statistics Finder groups by up to three pivots, so a returned element carries
    one URN per pivot in its ``pivotValues`` array (here: CAMPAIGN, CREATIVE). Only
    raw API fields are included; the connector derives ``string_of_pivot_values``
    (a comma-join of ``pivotValues``), ``end_date``, and ``start_date`` itself.
    """
    return {
        "dateRange": {
            "start": {"year": 2024, "month": 6, "day": 1},
            "end": {"year": 2024, "month": 6, "day": 1},
        },
        "pivotValues": [
            f"urn:li:sponsoredCampaign:{campaign_id}",
            f"urn:li:sponsoredCreative:{creative_id}",
        ],
        "impressions": impressions,
        "clicks": clicks,
        "costInLocalCurrency": "10.00",
        "costInUsd": "10.00",
    }


def _get_custom_statistics_report_config() -> list:
    """
    Returns the ad_statistics_reports config required for the custom_statistics_report stream.

    The custom_statistics_report stream uses a ConfigComponentsResolver that reads from the
    ad_statistics_reports config. Without this config, the stream produces zero slices and makes
    no HTTP requests.

    The stream name is generated as "custom_{{name}}" from the config entry's name field, so
    "name": "statistics_report" produces stream "custom_statistics_report".
    """
    return [
        {
            "name": "statistics_report",
            "pivots": ["CAMPAIGN", "CREATIVE"],
            "time_granularity": "DAILY",
        }
    ]


@freezegun.freeze_time("2024-06-15T00:00:00Z")
class TestCustomStatisticsReportStream(TestCase):
    """
    Tests for the LinkedIn Ads 'custom_statistics_report' stream.

    This is a substream of campaigns that mirrors custom_analytics_report but targets LinkedIn's
    Statistics Finder. It uses:
    - NoPagination (analytics endpoints don't paginate)
    - DatetimeBasedCursor with 30-day steps
    - Transformations that add 'sponsoredCampaign' and 'pivot' fields
    - CustomRecordExtractor and CustomErrorHandler (LinkedInAdsErrorHandler)
    - SubstreamPartitionRouter to iterate over parent campaigns
    - A ConfigComponentsResolver that reads from the ad_statistics_reports config

    Unlike the Analytics Finder, requests send q=statistics with a pivots=List(...) parameter
    (up to three categories) and no single pivot parameter.
    """

    @HttpMocker()
    def test_full_refresh_with_single_parent_campaign(self, http_mocker: HttpMocker):
        """
        Given: A parent campaign with statistics data and ad_statistics_reports config
        When: Running a full refresh sync
        Then: The connector fetches statistics for the campaign and joins the multi-pivot values
        """
        config = ConfigBuilder().with_start_date("2024-06-01").with_ad_statistics_reports(_get_custom_statistics_report_config()).build()

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
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_statistics_record(1001, 2001)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.stream == _STREAM_NAME
        # The extractor joins the multiple pivot URNs (one per pivot) into a single key.
        assert output.records[0].record.data["string_of_pivot_values"] == "urn:li:sponsoredCampaign:1001,urn:li:sponsoredCreative:2001"

    @HttpMocker()
    def test_statistics_finder_request_uses_pivots(self, http_mocker: HttpMocker):
        """
        Given: ad_statistics_reports config with two pivot categories
        When: Running a full refresh sync
        Then: Requests use q=statistics with pivots=List(CAMPAIGN,CREATIVE) and no single pivot param
        """
        config = ConfigBuilder().with_start_date("2024-06-01").with_ad_statistics_reports(_get_custom_statistics_report_config()).build()

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
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_statistics_record(1001, 2001)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.stream == _STREAM_NAME

        analytics_requests = [
            request for request in http_mocker._mocker.request_history if urlparse(request.url).path == "/rest/adAnalytics"
        ]
        statistics_requests = []
        for request in analytics_requests:
            query_params = parse_qs(urlparse(request.url).query)
            if query_params.get("q") == ["statistics"]:
                statistics_requests.append(query_params)

        assert statistics_requests
        assert all(query_params["pivots"] == ["List(CAMPAIGN,CREATIVE)"] for query_params in statistics_requests)
        assert all("pivot" not in query_params for query_params in statistics_requests)

    @HttpMocker()
    def test_transformations_applied(self, http_mocker: HttpMocker):
        """
        Given: Statistics data from the API with ad_statistics_reports config
        When: Running a full refresh sync
        Then: Records have 'sponsoredCampaign' and 'pivot' fields added by the manifest transformations

        Note: 'sponsoredCampaign' is populated from the parent partition. The 'pivot' field is seeded
        with the placeholder 'DYNAMIC_FIELD' in the stream template; the DynamicDeclarativeStream components
        mapping targets the stream-level field_path ["transformations", "1", "fields", "0", "value"] and
        replaces it with the comma-joined configured pivots, so the resolved value is 'CAMPAIGN,CREATIVE'.
        """
        config = ConfigBuilder().with_start_date("2024-06-01").with_ad_statistics_reports(_get_custom_statistics_report_config()).build()

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
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_statistics_record(1001, 2001)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record_data = output.records[0].record.data

        assert record_data["sponsoredCampaign"] == "1001"
        assert record_data["pivot"] == "CAMPAIGN,CREATIVE"  # comma-joined configured pivots, resolved by the components mapping

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """
        Given: No parent campaigns and ad_statistics_reports config
        When: Running a full refresh sync
        Then: No child requests are made and zero records are returned without errors
        """
        config = ConfigBuilder().with_start_date("2024-06-01").with_ad_statistics_reports(_get_custom_statistics_report_config()).build()

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
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Given: No prior state and ad_statistics_reports config
        When: Running an incremental sync
        Then: Records carry the derived end_date cursor and a state message is emitted
        """
        config = ConfigBuilder().with_start_date("2024-06-01").with_ad_statistics_reports(_get_custom_statistics_report_config()).build()

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
            LinkedInAdsAnalyticsResponseBuilder().with_records([_create_statistics_record(1001, 2001)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["end_date"] == "2024-06-01"   # derived from dateRange.end
        assert len(output.state_messages) > 0