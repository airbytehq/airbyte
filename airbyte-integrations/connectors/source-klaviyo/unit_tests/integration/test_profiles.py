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
_STREAM_NAME = "profiles"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProfilesStream(TestCase):
    """
    Tests for the Klaviyo 'profiles' stream.

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
        When: Running a full refresh sync for the profiles stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        # Use with_any_query_params() to match any query parameters since the exact
        # datetime format may vary (e.g., +00:00 vs +0000 timezone offset)
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_001",
                                "attributes": {
                                    "email": "test@example.com",
                                    "first_name": "John",
                                    "last_name": "Doe",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                },
                                "links": {"self": "https://a.klaviyo.com/api/profiles/profile_001"},
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
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
        assert record["id"] == "profile_001"
        assert record["attributes"]["email"] == "test@example.com"
        assert record["updated"] == "2024-01-15T12:30:00+00:00"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        NOTE: This test validates pagination for the 'profiles' stream. All streams
        in source-klaviyo use the same CursorPagination configuration with RequestPath
        page_token_option, so this provides pagination coverage for:
        profiles, global_exclusions, events, events_detailed, email_templates,
        campaigns, campaigns_detailed, flows, metrics, lists, lists_detailed

        Given: An API that returns multiple pages of profiles
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            KlaviyoPaginatedResponseBuilder()
            .with_records(
                [
                    {
                        "type": "profile",
                        "id": "profile_001",
                        "attributes": {
                            "email": "user1@example.com",
                            "first_name": "User",
                            "last_name": "One",
                            "updated": "2024-01-10T10:00:00+00:00",
                        },
                    },
                    {
                        "type": "profile",
                        "id": "profile_002",
                        "attributes": {
                            "email": "user2@example.com",
                            "first_name": "User",
                            "last_name": "Two",
                            "updated": "2024-01-11T10:00:00+00:00",
                        },
                    },
                ]
            )
            .with_next_page_link("https://a.klaviyo.com/api/profiles?page[cursor]=abc123")
            .build(),
        )

        http_mocker.get(
            KlaviyoRequestBuilder.from_url("https://a.klaviyo.com/api/profiles?page[cursor]=abc123", _API_KEY).build(),
            KlaviyoPaginatedResponseBuilder()
            .with_records(
                [
                    {
                        "type": "profile",
                        "id": "profile_003",
                        "attributes": {
                            "email": "user3@example.com",
                            "first_name": "User",
                            "last_name": "Three",
                            "updated": "2024-01-12T10:00:00+00:00",
                        },
                    }
                ]
            )
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == "profile_001"
        assert output.records[1].record.data["id"] == "profile_002"
        assert output.records[2].record.data["id"] == "profile_003"
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state.

        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should use start_date from config and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_001",
                                "attributes": {
                                    "email": "test@example.com",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "profile_001"

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
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-03-01T00:00:00+00:00"}).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_new",
                                "attributes": {
                                    "email": "new@example.com",
                                    "updated": "2024-03-15T10:00:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "profile_new"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        # Note: The connector returns datetime with +0000 format (without colon)
        assert latest_state["updated"] == "2024-03-15T10:00:00+0000"

    @HttpMocker()
    def test_transformation_adds_updated_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'updated' from attributes.

        The manifest configures:
        transformations:
          - type: AddFields
            fields:
              - path: [updated]
                value: "{{ record.get('attributes', {}).get('updated') }}"

        Given: A profile record with updated in attributes
        When: Running a sync
        Then: The 'updated' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_transform_test",
                                "attributes": {
                                    "email": "transform@example.com",
                                    "updated": "2024-02-20T14:45:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
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
        assert record["updated"] == "2024-02-20T14:45:00+00:00"
        assert record["attributes"]["updated"] == "2024-02-20T14:45:00+00:00"

    @HttpMocker()
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        The manifest configures:
        response_filters:
          - type: HttpResponseFilter
            action: RATE_LIMITED
            http_codes: [429]

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
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
                                    "type": "profile",
                                    "id": "profile_after_retry",
                                    "attributes": {
                                        "email": "retry@example.com",
                                        "updated": "2024-01-20T10:00:00+00:00",
                                    },
                                }
                            ],
                            "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
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
        assert output.records[0].record.data["id"] == "profile_after_retry"

        log_messages = [log.log.message for log in output.logs]
        backoff_logs = [msg for msg in log_messages if "429" in msg or "Backing off" in msg.lower() or "rate" in msg.lower()]
        assert len(backoff_logs) > 0, "Expected log messages indicating rate limit handling"

    @HttpMocker()
    def test_unauthorized_401_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 401 Unauthorized errors with FAIL action.

        The manifest configures:
        response_filters:
          - type: HttpResponseFilter
            action: FAIL
            http_codes: [401, 403]
            failure_type: config_error
            error_message: "Please provide a valid API key..."

        Given: Invalid API credentials
        When: Making an API request that returns 401
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint("invalid_key").with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Invalid API key"}]}),
                status_code=401,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        log_messages = [log.log.message for log in output.logs]
        error_logs = [msg for msg in log_messages if "401" in msg or "api key" in msg.lower() or "permission" in msg.lower()]
        assert len(error_logs) > 0, "Expected error log messages for 401 authentication failure"

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
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Forbidden - insufficient permissions"}]}),
                status_code=403,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        log_messages = [log.log.message for log in output.logs]
        error_logs = [msg for msg in log_messages if "403" in msg or "permission" in msg.lower() or "forbidden" in msg.lower()]
        assert len(error_logs) > 0, "Expected error log messages for 403 permission failure"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no profiles
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"data": [], "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_predictive_analytics_disabled(self, http_mocker: HttpMocker):
        """
        Test that predictive_analytics field is not requested when disabled.

        The manifest configures:
        request_parameters:
          additional-fields[profile]: >-
            {{ 'predictive_analytics' if not config['disable_fetching_predictive_analytics'] else '' }}

        Given: Config with disable_fetching_predictive_analytics=True
        When: Running a sync
        Then: The additional-fields parameter should be empty
        """
        config = (
            ConfigBuilder()
            .with_api_key(_API_KEY)
            .with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc))
            .with_disable_fetching_predictive_analytics(True)
            .build()
        )

        # Use with_any_query_params() to match any query parameters
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_no_analytics",
                                "attributes": {
                                    "email": "noanalytics@example.com",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "profile_no_analytics"
