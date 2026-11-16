# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "accounts"


def _create_account_record(account_id: int, name: str = "Test Account") -> dict:
    return {
        "id": account_id,
        "name": name,
        "type": "BUSINESS",
        "status": "ACTIVE",
        "currency": "USD",
        "reference": f"ref_{account_id}",
        "changeAuditStamps": {"created": {"time": 1479402003000}, "lastModified": {"time": 1479402004534}},
        "servingStatuses": ["RUNNABLE"],
        "notifiedOnCreativeApproval": False,
        "notifiedOnCreativeRejection": False,
        "notifiedOnEndOfCampaign": False,
        "notifiedOnNewFeaturesEnabled": False,
        "test": False,
        "version": {"versionTag": "1"},
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestAccountsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'accounts' stream.

    This is the parent stream for most other streams. It uses:
    - CursorPagination with pageToken
    - DpathExtractor with AddFields audit-stamp conversion
    - DefaultErrorHandler
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of accounts.

        Given: A configured LinkedIn Ads connector
        When: Running a full refresh sync for the accounts stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(123456789, "Acme Corporation")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 123456789
        assert record["name"] == "Acme Corporation"
        assert record["status"] == "ACTIVE"
        assert record["currency"] == "USD"
        assert record["created"] == "2016-11-17T17:00:03+00:00"
        assert record["lastModified"] == "2016-11-17T17:00:04+00:00"
        assert "changeAuditStamps" not in record

    @HttpMocker()
    def test_missing_audit_stamps(self, http_mocker: HttpMocker):
        config = ConfigBuilder().build()
        records = [_create_account_record(account_id) for account_id in range(1, 5)]
        records[0].pop("changeAuditStamps")
        records[1]["changeAuditStamps"] = {"created": {"time": 1479402003000}}
        records[2]["changeAuditStamps"] = None
        records[3]["changeAuditStamps"] = {"created": {"time": None}, "lastModified": {}}
        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(records),
        )
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(get_source(config=config), config=config, catalog=catalog)
        assert len(output.records) == 4
        for index, message in enumerate(output.records):
            record = message.record.data
            assert "changeAuditStamps" not in record
            assert "lastModified" not in record
            if index == 1:
                assert record["created"] == "2016-11-17T17:00:03+00:00"
            else:
                assert "created" not in record

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        NOTE: This test validates CursorPagination for the 'accounts' stream.
        The same pagination pattern is used by campaigns, campaign_groups, creatives,
        lead_forms, and lead_form_responses streams.

        Given: An API that returns multiple pages of accounts
        When: Running a full refresh sync
        Then: The connector should follow pagination tokens and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder()
            .with_records(
                [
                    _create_account_record(111111111, "Account 1"),
                    _create_account_record(222222222, "Account 2"),
                ]
            )
            .with_next_page_token("next_page_token_123")
            .build(),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint()
            .with_q("search")
            .with_page_size(500)
            .with_page_token("next_page_token_123")
            .build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(333333333, "Account 3")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == 111111111
        assert output.records[1].record.data["id"] == 222222222
        assert output.records[2].record.data["id"] == 333333333
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no accounts
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
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
    def test_account_id_filter(self, http_mocker: HttpMocker):
        """
        Test that connector filters accounts by account_ids config.

        Given: A config with specific account_ids
        When: Running a full refresh sync
        Then: Only accounts matching the filter should be returned
        """
        config = ConfigBuilder().with_account_ids([123456789]).build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_account_record(123456789, "Matching Account"),
                    _create_account_record(987654321, "Non-Matching Account"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 123456789
        assert output.records[0].record.data["name"] == "Matching Account"

    @HttpMocker()
    def test_server_error_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 500 server errors with retry.

        Given: An API that returns a 500 error then succeeds
        When: Making an API request
        Then: The connector should retry and eventually succeed
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            [
                HttpResponse(
                    body=json.dumps({"message": "Internal Server Error"}),
                    status_code=500,
                ),
                LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(123456789, "Account After Retry")]),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 123456789

    @HttpMocker()
    def test_rate_limit_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with retry.

        Given: An API that returns a 429 rate limit error then succeeds
        When: Making an API request
        Then: The connector should respect the rate limit and retry
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            [
                HttpResponse(
                    body=json.dumps({"message": "Rate limit exceeded"}),
                    status_code=429,
                    headers={"Retry-After": "1"},
                ),
                LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(123456789, "Account After Rate Limit")]),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 123456789
