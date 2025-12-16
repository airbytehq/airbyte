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
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder
from mock_server.response_builder import KlaviyoPaginatedResponseBuilder


_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "email_templates"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestEmailTemplatesStream(TestCase):
    """
    Tests for the Klaviyo 'email_templates' stream.

    Stream configuration from manifest.yaml:
    - Incremental sync with DatetimeBasedCursor on 'updated' field
    - Pagination: CursorPagination with page[size]=100
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Transformations: AddFields to extract 'updated' from attributes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.

        Given: A configured Klaviyo connector
        When: Running a full refresh sync for the email_templates stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "template",
                                "id": "template_001",
                                "attributes": {
                                    "name": "Welcome Email",
                                    "editor_type": "CODE",
                                    "html": "<html><body>Welcome!</body></html>",
                                    "text": "Welcome!",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/templates", "next": None},
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
        assert record["id"] == "template_001"
        assert record["attributes"]["name"] == "Welcome Email"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Note: This test also validates pagination behavior for other streams using the same
        CursorPagination pattern (profiles, events, flows, metrics, lists).

        Given: An API that returns multiple pages of templates
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Use a single mock with multiple responses to avoid ambiguity in mock matching.
        # The first response includes a next_page_link, the second response has no next link.
        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY).with_any_query_params().build(),
            [
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "template",
                            "id": "template_001",
                            "attributes": {
                                "name": "Template 1",
                                "editor_type": "CODE",
                                "created": "2024-05-31T10:00:00+00:00",
                                "updated": "2024-05-31T10:00:00+00:00",
                            },
                        }
                    ]
                )
                .with_next_page_link("https://a.klaviyo.com/api/templates?page[cursor]=abc123")
                .build(),
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "template",
                            "id": "template_002",
                            "attributes": {
                                "name": "Template 2",
                                "editor_type": "DRAG_AND_DROP",
                                "created": "2024-05-31T11:00:00+00:00",
                                "updated": "2024-05-31T11:00:00+00:00",
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
        assert output.records[0].record.data["id"] == "template_001"
        assert output.records[1].record.data["id"] == "template_002"

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state.

        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should use start_date from config and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "template",
                                "id": "template_001",
                                "attributes": {
                                    "name": "Welcome Email",
                                    "editor_type": "CODE",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/templates", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "template_001"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        assert "updated" in latest_state

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with a prior state from previous sync.

        Given: A previous sync state with an updated cursor value
        When: Running an incremental sync
        Then: The connector should use the state cursor and return only new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-05-31T00:00:00+00:00"}).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "template",
                                "id": "template_new",
                                "attributes": {
                                    "name": "New Template",
                                    "editor_type": "CODE",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T10:00:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/templates", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "template_new"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        # Note: The connector returns datetime with +0000 format (without colon)
        assert latest_state["updated"] == "2024-05-31T10:00:00+0000"

    @HttpMocker()
    def test_transformation_adds_updated_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'updated' from attributes.

        Given: A template record with updated in attributes
        When: Running a sync
        Then: The 'updated' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "template",
                                "id": "template_transform_test",
                                "attributes": {
                                    "name": "Transform Test",
                                    "editor_type": "CODE",
                                    "created": "2024-05-31T10:00:00+00:00",
                                    "updated": "2024-05-31T14:45:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/templates", "next": None},
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
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
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
                                    "type": "template",
                                    "id": "template_after_retry",
                                    "attributes": {
                                        "name": "After Retry",
                                        "editor_type": "CODE",
                                        "created": "2024-05-31T10:00:00+00:00",
                                        "updated": "2024-05-31T10:00:00+00:00",
                                    },
                                }
                            ],
                            "links": {"self": "https://a.klaviyo.com/api/templates", "next": None},
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
        assert output.records[0].record.data["id"] == "template_after_retry"

        log_messages = [log.log.message for log in output.logs]
        # Check for backoff log message pattern
        assert any(
            "Backing off" in msg and "UserDefinedBackoffException" in msg and "429" in msg for msg in log_messages
        ), "Expected backoff log message for 429 rate limit"
        # Check for retry/sleeping log message pattern
        assert any(
            "Sleeping for" in msg and "seconds" in msg for msg in log_messages
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

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint("invalid_key")
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
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
        assert any(
            expected_error_message in msg for msg in log_messages
        ), f"Expected error message '{expected_error_message}' in logs for 401 authentication failure"

    @HttpMocker()
    def test_forbidden_403_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 403 Forbidden errors with FAIL action.

        The manifest configures 403 errors with action: FAIL, which means the connector
        should fail the sync when permission errors occur.

        Given: API credentials with insufficient permissions
        When: Making an API request that returns 403
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Forbidden - insufficient permissions"}]}),
                status_code=403,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        expected_error_message = "Please provide a valid API key and make sure it has permissions to read specified streams."
        log_messages = [log.log.message for log in output.logs]
        assert any(
            expected_error_message in msg for msg in log_messages
        ), f"Expected error message '{expected_error_message}' in logs for 403 permission failure"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no templates
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.templates_endpoint(_API_KEY)
            .with_query_params(
                {
                    "filter": "greater-than(updated,2024-05-31T00:00:00+0000)",
                    "sort": "updated",
                }
            )
            .build(),
            HttpResponse(
                body=json.dumps({"data": [], "links": {"self": "https://a.klaviyo.com/api/templates", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
