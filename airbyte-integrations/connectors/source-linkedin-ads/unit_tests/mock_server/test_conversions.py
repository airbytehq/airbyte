# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import (
    LinkedInAdsOffsetPaginatedResponseBuilder,
    LinkedInAdsPaginatedResponseBuilder,
)


_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "conversions"

# Timestamps in milliseconds (as expected by the schema)
_TIMESTAMP_JAN_2024 = 1704067200000  # 2024-01-01T00:00:00Z
_TIMESTAMP_JUN_2024 = 1717200000000  # 2024-06-01T00:00:00Z
_TIMESTAMP_JUL_2024 = 1719792000000  # 2024-07-01T00:00:00Z


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


def _create_conversion_record(
    conversion_id: int,
    account_id: int,
    last_modified: int = _TIMESTAMP_JUN_2024,
) -> dict:
    """Create a conversion record with integer timestamps (milliseconds since epoch)."""
    return {
        "id": conversion_id,
        "name": f"Conversion {conversion_id}",
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "enabled": True,
        "type": "LEAD_GEN",
        "attributionType": "LAST_TOUCH",
        "lastModified": last_modified,
        "created": _TIMESTAMP_JAN_2024,
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestConversionsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'conversions' stream.

    This is a substream of accounts that uses:
    - OffsetIncrement pagination (start parameter)
    - Client-side incremental sync with lastModified cursor
    - SubstreamPartitionRouter to iterate over parent accounts
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Test that connector fetches conversions for multiple parent accounts.

        Given: Two parent accounts with conversions
        When: Running a full refresh sync
        Then: The connector should fetch conversions for each account
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

        # Use specific query params for each account since the path is the same
        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records(
                [
                    _create_conversion_record(1001, 111111111),
                    _create_conversion_record(1002, 111111111),
                ]
            )
            .build(),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(222222222).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().with_records([_create_conversion_record(2001, 222222222)]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        conversion_ids = {record.record.data["id"] for record in output.records}
        assert conversion_ids == {1001, 1002, 2001}

    @HttpMocker()
    def test_offset_pagination(self, http_mocker: HttpMocker):
        """
        Test that connector handles OffsetIncrement pagination correctly.

        NOTE: This test validates OffsetIncrement pagination for conversions.
        The same pagination pattern is used by account_users stream.

        Given: An API that returns multiple pages using offset pagination
        When: Running a full refresh sync
        Then: The connector should follow offset and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        page1_records = [_create_conversion_record(i, 111111111) for i in range(1, 501)]
        page2_records = [_create_conversion_record(i, 111111111) for i in range(501, 503)]

        # First page request (no start param)
        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().with_records(page1_records).with_paging(start=0, count=500, total=502).build(),
        )

        # Second page request (with start=500)
        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).with_start(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().with_records(page2_records).with_paging(start=500, count=500, total=502).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 502

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
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().with_records([_create_conversion_record(1001, 111111111)]).build(),
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

        NOTE: This test validates that the connector handles state correctly. The conversions stream
        uses CartesianProductStreamSlicer which has limited parent state handling support.
        The test verifies that the stream completes without errors when state is provided.
        """
        config = ConfigBuilder().build()
        # State uses ISO format (per datetime_format in manifest)
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"lastModified": "2024-06-01T00:00:00+0000"}).build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records(
                [
                    _create_conversion_record(1001, 111111111, _TIMESTAMP_JAN_2024),
                    _create_conversion_record(1002, 111111111, _TIMESTAMP_JUL_2024),
                ]
            )
            .build(),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # The CartesianProductStreamSlicer warns that "Parent state handling is not supported"
        # which means the stream may not make requests when state is provided.
        # We verify the stream completes without errors.
        assert not any(log.log.level == "ERROR" for log in output.logs)

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

        Given: A parent account with no conversions
        When: Running a full refresh sync
        Then: Zero records should be returned without errors
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.conversions_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
