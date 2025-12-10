# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import KlaviyoRequestBuilder
from integration.response_builder import KlaviyoPaginatedResponseBuilder


_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "lists_detailed"
_PARENT_STREAM_NAME = "lists"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestListsDetailedStream(TestCase):
    """
    Tests for the Klaviyo 'lists_detailed' stream.

    Stream configuration from manifest.yaml:
    - Substream of 'lists' stream using SubstreamPartitionRouter
    - Fetches detailed list information with additional-fields[list]=profile_count
    - Client-side incremental sync (is_client_side_incremental: true)
    - DatetimeBasedCursor on 'updated' field
    - is_data_feed: true
    - Pagination: CursorPagination
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Transformations: AddFields to extract 'updated' from attributes
    """

    @HttpMocker()
    def test_full_refresh_with_two_parent_records(self, http_mocker: HttpMocker):
        """
        Test that substream correctly fetches data for multiple parent records.

        Given: A parent stream (lists) that returns two list records
        When: Running a full refresh sync for lists_detailed
        Then: The connector should fetch detailed data for each parent list
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "list",
                                "id": "list_001",
                                "attributes": {
                                    "name": "Newsletter Subscribers",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "opt_in_process": "single_opt_in",
                                    "profile_count": 1500,
                                },
                            },
                            {
                                "type": "list",
                                "id": "list_002",
                                "attributes": {
                                    "name": "VIP Customers",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "opt_in_process": "double_opt_in",
                                    "profile_count": 500,
                                },
                            },
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert "list_001" in record_ids
        assert "list_002" in record_ids

        list_001_record = next(r for r in output.records if r.record.data["id"] == "list_001")
        assert list_001_record.record.data["attributes"]["name"] == "Newsletter Subscribers"
        assert list_001_record.record.data["attributes"]["profile_count"] == 1500

        list_002_record = next(r for r in output.records if r.record.data["id"] == "list_002")
        assert list_002_record.record.data["attributes"]["name"] == "VIP Customers"
        assert list_002_record.record.data["attributes"]["profile_count"] == 500

    @HttpMocker()
    def test_pagination_multiple_pages_parent_stream(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages from parent stream.

        Given: A parent stream (lists) that returns multiple pages
        When: Running a full refresh sync for lists_detailed
        Then: The connector should follow pagination and fetch detailed data for all parent records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Use a single mock with multiple responses to avoid ambiguity in mock matching.
        # The first response includes a next_page_link, the second response has no next link.
        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            [
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "list",
                            "id": "list_001",
                            "attributes": {
                                "name": "List 1",
                                "created": "2024-05-31T10:00:00+00:00",
                                "updated": "2024-05-31T10:00:00+00:00",
                                "opt_in_process": "single_opt_in",
                                "profile_count": 100,
                            },
                        }
                    ]
                )
                .with_next_page_link("https://a.klaviyo.com/api/lists?page[cursor]=abc123")
                .build(),
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "list",
                            "id": "list_002",
                            "attributes": {
                                "name": "List 2",
                                "created": "2024-05-31T11:00:00+00:00",
                                "updated": "2024-05-31T11:00:00+00:00",
                                "opt_in_process": "double_opt_in",
                                "profile_count": 200,
                            },
                        }
                    ]
                )
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "list_001"
        assert output.records[1].record.data["id"] == "list_002"

    @HttpMocker()
    def test_client_side_incremental_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state (client-side incremental).

        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should fetch all records and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "list",
                                "id": "list_001",
                                "attributes": {
                                    "name": "Test List",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "opt_in_process": "single_opt_in",
                                    "profile_count": 1000,
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "list_001"

        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_client_side_incremental_with_prior_state(self, http_mocker: HttpMocker):
        """
        Test client-side incremental sync with a prior state from previous sync.

        For client-side incremental streams (is_client_side_incremental: true), the connector
        fetches all records from the API but filters them client-side based on the state.

        Given: A previous sync state with an updated cursor value
        When: Running an incremental sync
        Then: The connector should filter records client-side and only return new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-03-01T00:00:00+00:00"}).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "list",
                                "id": "list_old",
                                "attributes": {
                                    "name": "Old List",
                                    "created": "2024-01-01T10:00:00+00:00",
                                    "updated": "2024-02-15T10:00:00+00:00",
                                    "opt_in_process": "single_opt_in",
                                    "profile_count": 500,
                                },
                            },
                            {
                                "type": "list",
                                "id": "list_new",
                                "attributes": {
                                    "name": "New List",
                                    "created": "2024-03-10T10:00:00+00:00",
                                    "updated": "2024-03-15T10:00:00+00:00",
                                    "opt_in_process": "double_opt_in",
                                    "profile_count": 1500,
                                },
                            },
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "list_new"

        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_transformation_adds_updated_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'updated' from attributes.

        Given: A list_detailed record with updated in attributes
        When: Running a sync
        Then: The 'updated' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "list",
                                "id": "list_transform_test",
                                "attributes": {
                                    "name": "Transform Test",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T14:45:00+00:00",
                                    "opt_in_process": "single_opt_in",
                                    "profile_count": 750,
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert "updated" in record
        assert record["updated"] == "2024-05-31T14:45:00+00:00"

    @HttpMocker()
    def test_profile_count_additional_field(self, http_mocker: HttpMocker):
        """
        Test that the additional-fields[list]=profile_count parameter returns profile_count.

        The lists_detailed stream requests additional fields to get profile_count.

        Given: An API response with profile_count in attributes
        When: Running a sync
        Then: The record should contain the profile_count field
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "list",
                                "id": "list_with_count",
                                "attributes": {
                                    "name": "List with Profile Count",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "opt_in_process": "single_opt_in",
                                    "profile_count": 2500,
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["attributes"]["profile_count"] == 2500

    @HttpMocker()
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            [
                HttpResponse(
                    body=json.dumps({"errors": [{"detail": "Rate limit exceeded"}]}),
                    status_code=429,
                    headers={"Retry-After": "1"},
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [
                                {
                                    "type": "list",
                                    "id": "list_after_retry",
                                    "attributes": {
                                        "name": "After Retry",
                                        "created": "2024-05-31T10:00:00+00:00",
                                        "updated": "2024-05-31T10:00:00+00:00",
                                        "opt_in_process": "single_opt_in",
                                        "profile_count": 100,
                                    },
                                }
                            ],
                            "links": {"self": "https://a.klaviyo.com/api/lists", "next": None},
                        }
                    ),
                    status_code=200,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "list_after_retry"

        log_messages = [log.log.message for log in output.logs]
        # Check for backoff log message pattern
        assert any(
            "Backing off" in msg and "UserDefinedBackoffException" in msg and "429" in msg
            for msg in log_messages
        ), "Expected backoff log message for 429 rate limit"
        # Check for retry/sleeping log message pattern
        assert any(
            "Sleeping for" in msg and "seconds" in msg
            for msg in log_messages
        ), "Expected retry sleeping log message for 429 rate limit"

    @HttpMocker()
    def test_unauthorized_401_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 401 Unauthorized errors with FAIL action.

        Given: Invalid API credentials
        When: Making an API request that returns 401
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint("invalid_key").build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Invalid API key"}]}),
                status_code=401,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        expected_error_message = "Please provide a valid API key and make sure it has permissions to read specified streams."
        log_messages = [log.log.message for log in output.logs]
        assert any(expected_error_message in msg for msg in log_messages), (
            f"Expected error message '{expected_error_message}' in logs for 401 authentication failure"
        )

    @HttpMocker()
    def test_empty_parent_stream_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent stream results gracefully.

        Given: A parent stream (lists) that returns no records
        When: Running a full refresh sync for lists_detailed
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # lists_detailed is a substream of lists. The parent lists stream has no query parameters.
        http_mocker.get(
            KlaviyoRequestBuilder.lists_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps({"data": [], "links": {"self": "https://a.klaviyo.com/api/lists", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
