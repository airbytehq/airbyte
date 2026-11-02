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
_STREAM_NAME = "events_detailed"
_API_KEY = "test_api_key_abc123"
_START_DATE = datetime(2024, 5, 31, tzinfo=timezone.utc)
_TIME_WINDOW_FILTER = "greater-or-equal(datetime,2024-05-31T00:00:00+0000),less-than(datetime,2024-06-01T12:00:00+0000)"


def _events_request(filter_expr: str):
    """Build an exact-match request for the events_detailed stream, discriminating on the filter query param."""
    return (
        KlaviyoRequestBuilder.events_endpoint(_API_KEY)
        .with_include("metric,attributions")
        .with_fields_metric("name")
        .with_filter(filter_expr)
        .with_sort("datetime")
        .build()
    )


def _events_response(record_id: str, metric_id: str) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "data": [
                    {
                        "type": "event",
                        "id": record_id,
                        "attributes": {
                            "timestamp": "2024-05-31T10:00:00+00:00",
                            "datetime": "2024-05-31T10:00:00+00:00",
                            "uuid": f"uuid-{record_id}",
                            "event_properties": {},
                        },
                        "relationships": {"metric": {"data": {"type": "metric", "id": metric_id}}, "attributions": {"data": []}},
                    }
                ],
                "included": [{"type": "metric", "id": metric_id, "attributes": {"name": f"Metric {metric_id}"}}],
                "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
            }
        ),
        status_code=200,
    )


@freezegun.freeze_time(_NOW.isoformat())
class TestEventsDetailedStream(TestCase):
    """
    Tests for the Klaviyo 'events_detailed' stream.

    Stream configuration from manifest.yaml:
    - Uses CustomRecordExtractor to flatten included metric data into event records
    - Incremental sync with DatetimeBasedCursor on 'datetime' field
    - Request parameters: fields[event], fields[metric], include=metric
    - Pagination: CursorPagination
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Transformations: AddFields to extract 'datetime' from attributes
    """

    @HttpMocker()
    def test_full_refresh_with_included_metrics(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with included metric data.

        The CustomRecordExtractor flattens the included metric data into each event record.

        Given: An API response with events and included metrics
        When: Running a full refresh sync
        Then: The connector should return events with metric data merged in
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        # Using with_any_query_params() to handle the dynamic date range filter
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "event",
                                "id": "event_001",
                                "attributes": {
                                    "timestamp": "2024-05-31T10:30:00+00:00",
                                    "datetime": "2024-05-31T10:30:00+00:00",
                                    "uuid": "550e8400-e29b-41d4-a716-446655440000",
                                    "event_properties": {"value": 99.99, "currency": "USD"},
                                },
                                "relationships": {
                                    "metric": {"data": {"type": "metric", "id": "metric_001"}},
                                    "attributions": {"data": []},
                                },
                            }
                        ],
                        "included": [
                            {
                                "type": "metric",
                                "id": "metric_001",
                                "attributes": {
                                    "name": "Placed Order",
                                    "created": "2023-01-01T00:00:00+00:00",
                                    "updated": "2024-01-01T00:00:00+00:00",
                                    "integration": {"id": "integration_001", "name": "Shopify"},
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
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
        assert record["id"] == "event_001"
        assert record["attributes"]["uuid"] == "550e8400-e29b-41d4-a716-446655440000"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of events with included metrics
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Use a single mock with multiple responses to avoid ambiguity in mock matching.
        # The first response includes a next link, the second response has no next link.
        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            [
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [
                                {
                                    "type": "event",
                                    "id": "event_001",
                                    "attributes": {
                                        "timestamp": "2024-05-31T10:00:00+00:00",
                                        "datetime": "2024-05-31T10:00:00+00:00",
                                        "uuid": "uuid-001",
                                        "event_properties": {},
                                    },
                                    "relationships": {"metric": {"data": {"type": "metric", "id": "m1"}}, "attributions": {"data": []}},
                                }
                            ],
                            "included": [{"type": "metric", "id": "m1", "attributes": {"name": "Metric 1"}}],
                            "links": {
                                "self": "https://a.klaviyo.com/api/events",
                                "next": "https://a.klaviyo.com/api/events?page[cursor]=abc123",
                            },
                        }
                    ),
                    status_code=200,
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [
                                {
                                    "type": "event",
                                    "id": "event_002",
                                    "attributes": {
                                        "timestamp": "2024-05-31T11:00:00+00:00",
                                        "datetime": "2024-05-31T11:00:00+00:00",
                                        "uuid": "uuid-002",
                                        "event_properties": {},
                                    },
                                    "relationships": {"metric": {"data": {"type": "metric", "id": "m2"}}, "attributions": {"data": []}},
                                }
                            ],
                            "included": [{"type": "metric", "id": "m2", "attributes": {"name": "Metric 2"}}],
                            "links": {"self": "https://a.klaviyo.com/api/events?page[cursor]=abc123", "next": None},
                        }
                    ),
                    status_code=200,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "event_001"
        assert output.records[1].record.data["id"] == "event_002"

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state.

        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should use start_date from config and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "event",
                                "id": "event_001",
                                "attributes": {
                                    "timestamp": "2024-05-31T10:30:00+00:00",
                                    "datetime": "2024-05-31T10:30:00+00:00",
                                    "uuid": "uuid-001",
                                    "event_properties": {},
                                },
                                "relationships": {"metric": {"data": {"type": "metric", "id": "m1"}}, "attributions": {"data": []}},
                            }
                        ],
                        "included": [{"type": "metric", "id": "m1", "attributes": {"name": "Metric 1"}}],
                        "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "event_001"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        # With ListPartitionRouter, state is nested under "state" key
        assert "datetime" in latest_state.get("state", latest_state)

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with a prior state from previous sync.

        Given: A previous sync state with a datetime cursor value
        When: Running an incremental sync
        Then: The connector should use the state cursor and return only new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"datetime": "2024-03-01T00:00:00+00:00"}).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "event",
                                "id": "event_new",
                                "attributes": {
                                    "timestamp": "2024-05-31T10:00:00+00:00",
                                    "datetime": "2024-05-31T10:00:00+00:00",
                                    "uuid": "uuid-new",
                                    "event_properties": {},
                                },
                                "relationships": {"metric": {"data": {"type": "metric", "id": "m1"}}, "attributions": {"data": []}},
                            }
                        ],
                        "included": [{"type": "metric", "id": "m1", "attributes": {"name": "Metric 1"}}],
                        "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "event_new"

        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_transformation_adds_datetime_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'datetime' from attributes.

        Given: An event record with datetime in attributes
        When: Running a sync
        Then: The 'datetime' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "event",
                                "id": "event_transform_test",
                                "attributes": {
                                    "timestamp": "2024-05-31T14:45:00+00:00",
                                    "datetime": "2024-05-31T14:45:00+00:00",
                                    "uuid": "uuid-transform",
                                    "event_properties": {"test": "value"},
                                },
                                "relationships": {"metric": {"data": {"type": "metric", "id": "m1"}}, "attributions": {"data": []}},
                            }
                        ],
                        "included": [{"type": "metric", "id": "m1", "attributes": {"name": "Metric 1"}}],
                        "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
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
        assert "datetime" in record
        assert record["datetime"] == "2024-05-31T14:45:00+00:00"

    @HttpMocker()
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
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
                                    "type": "event",
                                    "id": "event_after_retry",
                                    "attributes": {
                                        "timestamp": "2024-05-31T10:00:00+00:00",
                                        "datetime": "2024-05-31T10:00:00+00:00",
                                        "uuid": "uuid-retry",
                                        "event_properties": {},
                                    },
                                    "relationships": {"metric": {"data": {"type": "metric", "id": "m1"}}, "attributions": {"data": []}},
                                }
                            ],
                            "included": [{"type": "metric", "id": "m1", "attributes": {"name": "Metric 1"}}],
                            "links": {"self": "https://a.klaviyo.com/api/events", "next": None},
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
        assert output.records[0].record.data["id"] == "event_after_retry"

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

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint("invalid_key").with_any_query_params().build(),
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

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
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

        Given: An API that returns no events
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # events_detailed stream uses include, fields[metric], filter, and sort query parameters
        # Note: With chunking enabled (step: P7D), the filter now includes both start and end time bounds
        http_mocker.get(
            KlaviyoRequestBuilder.events_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"data": [], "included": [], "links": {"self": "https://a.klaviyo.com/api/events", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_multiple_event_metric_ids_produce_one_request_per_metric(self, http_mocker: HttpMocker):
        """
        Test that each configured metric ID becomes its own partition and request.

        Given: event_metric_ids set to "AAA111, BBB222" (with a stray space to be trimmed)
        When: Running a sync
        Then: One request per metric ID is issued with equals(metric_id,"<id>") appended to the filter,
              and the records of both partitions are emitted
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(_START_DATE).with_event_metric_ids("AAA111, BBB222").build()

        http_mocker.get(
            _events_request(f'{_TIME_WINDOW_FILTER},equals(metric_id,"AAA111")'),
            _events_response("event_aaa", "AAA111"),
        )
        http_mocker.get(
            _events_request(f'{_TIME_WINDOW_FILTER},equals(metric_id,"BBB222")'),
            _events_response("event_bbb", "BBB222"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert {record.record.data["id"] for record in output.records} == {"event_aaa", "event_bbb"}

    @HttpMocker()
    def test_single_event_metric_id_appends_one_filter_clause(self, http_mocker: HttpMocker):
        """
        Test that a single configured metric ID adds exactly one equals(metric_id,...) filter clause.

        Given: event_metric_ids set to a single metric ID
        When: Running a sync
        Then: Exactly one request is issued and its filter ends with a single equals(metric_id,...) clause
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(_START_DATE).with_event_metric_ids("AAA111").build()

        http_mocker.get(
            _events_request(f'{_TIME_WINDOW_FILTER},equals(metric_id,"AAA111")'),
            _events_response("event_aaa", "AAA111"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "event_aaa"

    @HttpMocker()
    def test_incremental_sync_migrates_legacy_flat_state(self, http_mocker: HttpMocker):
        """
        Guards legacy-state migration: connections that predate the ListPartitionRouter stored a flat
        {"datetime": ...} state, and the CDK must migrate it under the new per-partition cursor.

        Given: A flat legacy state and no event_metric_ids configured
        When: Running an incremental sync
        Then: The single request uses the state datetime as the greater-or-equal bound (not config start_date)
              and the filter carries no equals(metric_id,...) clause
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"datetime": "2024-05-28T00:00:00+0000"}).build()

        http_mocker.get(
            _events_request("greater-or-equal(datetime,2024-05-28T00:00:00+0000),less-than(datetime,2024-06-01T12:00:00+0000)"),
            _events_response("event_legacy", "m1"),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "event_legacy"
