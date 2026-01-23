# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
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
from .response_builder import (
    LinkedInAdsOffsetPaginatedResponseBuilder,
    LinkedInAdsPaginatedResponseBuilder,
)


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "account_users"
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


def _create_account_user_record(
    account_id: int,
    user_id: str,
    role: str = "ACCOUNT_BILLING_ADMIN",
    last_modified: str = "2024-06-01T00:00:00.000Z",
) -> dict:
    return {
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "user": user_id,
        "role": role,
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": last_modified,
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestAccountUsersStream(TestCase):
    """
    Tests for the LinkedIn Ads 'account_users' stream.

    This is a substream of accounts that uses:
    - OffsetIncrement pagination with 'start' parameter
    - Client-side incremental sync with lastModified cursor
    - SubstreamPartitionRouter to iterate over parent accounts
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Test that connector fetches account_users for multiple parent accounts.

        Given: Two parent accounts with account users
        When: Running a full refresh sync
        Then: The connector should fetch users for each account
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
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [
                    _create_account_user_record(111111111, "user_1", "ACCOUNT_BILLING_ADMIN"),
                    _create_account_user_record(111111111, "user_2", "VIEWER"),
                ],
                total=2,
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.account_users_endpoint(222222222).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [_create_account_user_record(222222222, "user_3", "CREATIVE_MANAGER")],
                total=1,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        user_ids = {record.record.data["user"] for record in output.records}
        assert user_ids == {"user_1", "user_2", "user_3"}
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_offset_pagination(self, http_mocker: HttpMocker):
        """
        Test that connector handles OffsetIncrement pagination correctly.

        NOTE: This test validates OffsetIncrement pagination for account_users.
        The same pagination pattern is used by the conversions stream.
        OffsetIncrement pagination stops when the number of records returned
        is less than the page_size (500). To test pagination, we need to return
        exactly page_size records on the first page.

        Given: An API that returns multiple pages using offset pagination
        When: Running a full refresh sync
        Then: The connector should follow offset pagination and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        first_page_records = [_create_account_user_record(111111111, f"user_{i}", "VIEWER") for i in range(500)]
        http_mocker.get(
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder().with_records(first_page_records).with_paging(start=0, count=500, total=502).build(),
        )

        second_page_records = [
            _create_account_user_record(111111111, "user_500", "ACCOUNT_BILLING_ADMIN"),
            _create_account_user_record(111111111, "user_501", "CREATIVE_MANAGER"),
        ]
        http_mocker.get(
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).with_start(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records(second_page_records)
            .with_paging(start=500, count=2, total=502)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 502
        user_ids = {record.record.data["user"] for record in output.records}
        assert "user_0" in user_ids
        assert "user_499" in user_ids
        assert "user_500" in user_ids
        assert "user_501" in user_ids

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
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [_create_account_user_record(111111111, "user_1", "ACCOUNT_BILLING_ADMIN")],
                total=1,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["user"] == "user_1"
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
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"lastModified": "2024-06-01T00:00:00+00:00"}).build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        old_user = _create_account_user_record(111111111, "old_user", "VIEWER", last_modified="2024-01-01T00:00:00.000Z")

        new_user = _create_account_user_record(111111111, "new_user", "ACCOUNT_BILLING_ADMIN", last_modified="2024-07-01T00:00:00.000Z")

        http_mocker.get(
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [old_user, new_user],
                total=2,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["user"] == "new_user"

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

        Given: A parent account with no users
        When: Running a full refresh sync
        Then: Zero records should be returned without errors
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.account_users_endpoint(111111111).with_count(500).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.empty_page(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
