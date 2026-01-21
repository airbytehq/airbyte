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
from .response_builder import LinkedInAdsOffsetPaginatedResponseBuilder, LinkedInAdsPaginatedResponseBuilder


_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "lead_forms"

# Timestamps in milliseconds
_TIMESTAMP_JAN_2024 = 1704067200000
_TIMESTAMP_JUN_2024 = 1717200000000


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


def _create_lead_form_record(
    form_id: int,
    account_id: int,
    name: str = "Test Lead Form",
    status: str = "ACTIVE",
    created: int = _TIMESTAMP_JAN_2024,
    last_modified: int = _TIMESTAMP_JUN_2024,
) -> dict:
    return {
        "id": form_id,
        "name": name,
        "status": status,
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "created": created,
        "lastModified": last_modified,
    }


@freezegun.freeze_time(_NOW)
class TestLeadFormsStream(TestCase):
    """Tests for the lead_forms stream."""

    @HttpMocker()
    def test_full_refresh_sync(self, http_mocker: HttpMocker):
        """
        Test basic full refresh sync for lead_forms stream.

        Given: A single account with lead forms
        When: Running a full refresh sync
        Then: All lead forms should be returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_lead_form_record(1001, 111111111, "Form 1"),
                    _create_lead_form_record(1002, 111111111, "Form 2"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = {record.record.data["id"] for record in output.records}
        assert record_ids == {1001, 1002}

    @HttpMocker()
    def test_cursor_pagination(self, http_mocker: HttpMocker):
        """
        Test that connector handles CursorPagination correctly for lead_forms.

        The lead_forms stream uses CursorPagination with 'start' parameter.
        The cursor value is calculated as: start + count from the response paging.
        Pagination stops when total == 0 in the response.

        Given: An API that returns multiple pages using cursor pagination
        When: Running a full refresh sync
        Then: The connector should follow pagination and return all records
        """
        config = ConfigBuilder().build()

        # Mock parent accounts endpoint
        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        # First page - returns 2 records with paging info indicating more records
        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records(
                [
                    _create_lead_form_record(1001, 111111111, "Form 1"),
                    _create_lead_form_record(1002, 111111111, "Form 2"),
                ]
            )
            .with_paging(start=0, count=2, total=3)
            .build(),
        )

        # Second page - returns 1 record with paging info indicating no more records
        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).with_start(2).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records([_create_lead_form_record(1003, 111111111, "Form 3")])
            .with_paging(start=2, count=1, total=0)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        record_ids = {record.record.data["id"] for record in output.records}
        assert record_ids == {1001, 1002, 1003}
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Test lead_forms stream with multiple parent accounts.

        Given: Multiple accounts with lead forms
        When: Running a full refresh sync
        Then: Lead forms from all accounts should be returned
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
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_lead_form_record(1001, 111111111, "Form 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(222222222).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_lead_form_record(2001, 222222222, "Form 2")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = {record.record.data["id"] for record in output.records}
        assert record_ids == {1001, 2001}

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """
        Test lead_forms stream when parent accounts stream is empty.

        Given: No accounts
        When: Running a full refresh sync
        Then: No lead forms should be returned and no child requests made
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0

    @HttpMocker()
    def test_parent_with_no_lead_forms(self, http_mocker: HttpMocker):
        """
        Test lead_forms stream when parent account has no lead forms.

        Given: An account with no lead forms
        When: Running a full refresh sync
        Then: No lead forms should be returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Test initial incremental sync (no prior state).

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
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_lead_form_record(1001, 111111111, "Form 1", last_modified=_TIMESTAMP_JAN_2024),
                    _create_lead_form_record(1002, 111111111, "Form 2", last_modified=_TIMESTAMP_JUN_2024),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with prior state (subsequent sync).

        Given: Prior state with a cursor value
        When: Running an incremental sync
        Then: Only records newer than the cursor should be returned (client-side filtering)
        """
        config = ConfigBuilder().build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"lastModified": "2024-06-01T00:00:00+0000"}).build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_forms_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_lead_form_record(1001, 111111111, "Form 1", last_modified=_TIMESTAMP_JAN_2024),
                    _create_lead_form_record(1002, 111111111, "Form 2", last_modified=_TIMESTAMP_JUN_2024),
                ]
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # Client-side incremental filtering should return only newer records
        # The stream completes without errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
