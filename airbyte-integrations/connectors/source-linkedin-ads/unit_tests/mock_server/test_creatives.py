# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "creatives"
_PARENT_STREAM_NAME = "accounts"


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
    last_modified_at: str = "2024-06-01T00:00:00+0000",
) -> dict:
    return {
        "id": creative_id,
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "name": name,
        "status": status,
        "type": "TEXT_AD",
        "campaign": f"urn:li:sponsoredCampaign:{creative_id}",
        "content": {"textAd": {"headline": "Test Headline", "description": "Test Description"}},
        "createdAt": "2024-01-01T00:00:00+0000",
        "lastModifiedAt": last_modified_at,
        "version": {"versionTag": "1"},
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestCreativesStream(TestCase):
    """
    Tests for the LinkedIn Ads 'creatives' stream.

    This is a substream of accounts that uses:
    - CursorPagination with pageToken
    - Client-side incremental sync with lastModifiedAt cursor
    - CompositeErrorHandler for 429, 500, 503 errors with RETRY action
    - SubstreamPartitionRouter to iterate over parent accounts
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Test that connector fetches creatives for multiple parent accounts.

        Given: Two parent accounts with creatives
        When: Running a full refresh sync
        Then: The connector should fetch creatives for each account
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_account_record(111111111, "Account 1"),
                    _create_account_record(222222222, "Account 2"),
                ]
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_creative_record(1001, 111111111, "Creative 1"),
                    _create_creative_record(1002, 111111111, "Creative 2"),
                ]
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(222222222).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 222222222, "Creative 3")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        creative_ids = {record.record.data["id"] for record in output.records}
        assert creative_ids == {1001, 1002, 2001}
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_cursor_pagination(self, http_mocker: HttpMocker):
        """
        Test that connector handles CursorPagination correctly.

        NOTE: This test validates CursorPagination for creatives.
        The same pagination pattern is used by accounts, campaigns, campaign_groups,
        lead_forms, and lead_form_responses streams.

        Given: An API that returns multiple pages using cursor pagination
        When: Running a full refresh sync
        Then: The connector should follow page tokens and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        # Provide multiple responses for the same endpoint to handle pagination
        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            [
                LinkedInAdsPaginatedResponseBuilder()
                .with_records(
                    [
                        _create_creative_record(1001, 111111111, "Creative 1"),
                        _create_creative_record(1002, 111111111, "Creative 2"),
                    ]
                )
                .with_next_page_token("next_page_token_abc")
                .build(),
                LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(1003, 111111111, "Creative 3")]),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        creative_ids = {record.record.data["id"] for record in output.records}
        assert creative_ids == {1001, 1002, 1003}

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Test incremental sync without prior state (first sync).

        Given: No prior state
        When: Running an incremental sync
        Then: All records should be returned and state should be emitted
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(1001, 111111111, "Creative 1")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1001
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with prior state (subsequent sync).

        Given: Prior state with a cursor value
        When: Running an incremental sync
        Then: Only records newer than the cursor should be returned (client-side filtering)
        """
        config = ConfigBuilder().build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"lastModifiedAt": "2024-06-01T00:00:00+0000"}).build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_creative_record(1001, 111111111, "Old Creative", "ACTIVE", "2024-01-01T00:00:00+0000"),
                    _create_creative_record(1002, 111111111, "New Creative", "ACTIVE", "2024-07-01T00:00:00+0000"),
                ]
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1002
        assert output.records[0].record.data["name"] == "New Creative"

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent stream gracefully.

        Given: No parent accounts
        When: Running a full refresh sync
        Then: No child requests should be made and zero records returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_parent_with_no_child_records(self, http_mocker: HttpMocker):
        """
        Test that connector handles parent with no child records gracefully.

        Given: A parent account with no creatives
        When: Running a full refresh sync
        Then: Zero records should be returned without errors
        """
        config = ConfigBuilder().build()

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
    def test_rate_limit_error_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit errors with RETRY action.

        NOTE: This test validates the CompositeErrorHandler for creatives.
        The error handler is configured to RETRY on 429, 500, and 503 errors.

        Given: An API that returns 429 rate limit error followed by success
        When: Running a full refresh sync
        Then: The connector should retry and eventually succeed
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        # First request returns 429, second request succeeds
        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            [
                HttpResponse(status_code=429, body='{"message": "Rate limit exceeded"}'),
                LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(1001, 111111111, "Creative 1")]),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1001
        # Verify no ERROR logs were produced (error was handled gracefully)
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_server_error_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 500/503 server errors with RETRY action.

        Given: An API that returns 500 server error followed by success
        When: Running a full refresh sync
        Then: The connector should retry and eventually succeed
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        # First request returns 500, second request succeeds
        http_mocker.get(
            LinkedInAdsRequestBuilder.creatives_endpoint(111111111).with_any_query_params().build(),
            [
                HttpResponse(status_code=500, body='{"message": "Internal server error"}'),
                LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(1001, 111111111, "Creative 1")]),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1001
        # Verify no ERROR logs were produced (error was handled gracefully)
        assert not any(log.log.level == "ERROR" for log in output.logs)
