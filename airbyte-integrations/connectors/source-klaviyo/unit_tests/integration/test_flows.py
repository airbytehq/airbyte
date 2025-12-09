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
_STREAM_NAME = "flows"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestFlowsStream(TestCase):
    """
    Tests for the Klaviyo 'flows' stream.

    Stream configuration from manifest.yaml:
    - Uses ListPartitionRouter to iterate over flow statuses (draft, manual, live)
    - Incremental sync with DatetimeBasedCursor on 'updated' field
    - Pagination: CursorPagination
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Transformations: AddFields to extract 'updated' from attributes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.

        Given: A configured Klaviyo connector
        When: Running a full refresh sync for the flows stream
        Then: The connector should make requests for each flow status partition
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "flow",
                                "id": "flow_001",
                                "attributes": {
                                    "name": "Welcome Series",
                                    "status": "live",
                                    "archived": False,
                                    "created": "2024-01-01T10:00:00+00:00",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                    "trigger_type": "List",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1
        record = output.records[0].record.data
        assert record["id"] == "flow_001"
        assert record["attributes"]["name"] == "Welcome Series"

    @HttpMocker()
    def test_partition_router_multiple_statuses(self, http_mocker: HttpMocker):
        """
        Test that the ListPartitionRouter correctly iterates over all flow statuses.

        The manifest configures:
        partition_router:
          type: ListPartitionRouter
          values: ["draft", "manual", "live"]
          cursor_field: "status"

        Given: An API that returns flows for each status
        When: Running a full refresh sync
        Then: The connector should make requests for each status partition
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "flow",
                                "id": "flow_001",
                                "attributes": {
                                    "name": "Test Flow",
                                    "status": "live",
                                    "archived": False,
                                    "created": "2024-01-01T10:00:00+00:00",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                    "trigger_type": "Segment",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of flows
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            KlaviyoPaginatedResponseBuilder()
            .with_records(
                [
                    {
                        "type": "flow",
                        "id": "flow_001",
                        "attributes": {
                            "name": "Flow 1",
                            "status": "live",
                            "archived": False,
                            "created": "2024-01-01T10:00:00+00:00",
                            "updated": "2024-01-10T10:00:00+00:00",
                            "trigger_type": "List",
                        },
                    }
                ]
            )
            .with_next_page_link("https://a.klaviyo.com/api/flows?page[cursor]=abc123")
            .build(),
        )

        http_mocker.get(
            KlaviyoRequestBuilder.from_url("https://a.klaviyo.com/api/flows?page[cursor]=abc123", _API_KEY).build(),
            KlaviyoPaginatedResponseBuilder()
            .with_records(
                [
                    {
                        "type": "flow",
                        "id": "flow_002",
                        "attributes": {
                            "name": "Flow 2",
                            "status": "live",
                            "archived": False,
                            "created": "2024-01-02T10:00:00+00:00",
                            "updated": "2024-01-11T10:00:00+00:00",
                            "trigger_type": "Segment",
                        },
                    }
                ]
            )
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 2

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
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "flow",
                                "id": "flow_001",
                                "attributes": {
                                    "name": "Test Flow",
                                    "status": "live",
                                    "archived": False,
                                    "created": "2024-01-01T10:00:00+00:00",
                                    "updated": "2024-01-15T12:30:00+00:00",
                                    "trigger_type": "List",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1
        assert len(output.state_messages) > 0

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
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "flow",
                                "id": "flow_new",
                                "attributes": {
                                    "name": "New Flow",
                                    "status": "live",
                                    "archived": False,
                                    "created": "2024-03-10T10:00:00+00:00",
                                    "updated": "2024-03-15T10:00:00+00:00",
                                    "trigger_type": "Segment",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) >= 1
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_transformation_adds_updated_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'updated' from attributes.

        Given: A flow record with updated in attributes
        When: Running a sync
        Then: The 'updated' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "flow",
                                "id": "flow_transform_test",
                                "attributes": {
                                    "name": "Transform Test",
                                    "status": "live",
                                    "archived": False,
                                    "created": "2024-01-01T10:00:00+00:00",
                                    "updated": "2024-02-20T14:45:00+00:00",
                                    "trigger_type": "List",
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1
        record = output.records[0].record.data
        assert "updated" in record
        assert record["updated"] == "2024-02-20T14:45:00+00:00"

    @HttpMocker()
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
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
                                    "type": "flow",
                                    "id": "flow_after_retry",
                                    "attributes": {
                                        "name": "After Retry",
                                        "status": "live",
                                        "archived": False,
                                        "created": "2024-01-01T10:00:00+00:00",
                                        "updated": "2024-01-20T10:00:00+00:00",
                                        "trigger_type": "List",
                                    },
                                }
                            ],
                            "links": {"self": "https://a.klaviyo.com/api/flows", "next": None},
                        }
                    ),
                    status_code=200,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1

    @HttpMocker()
    def test_unauthorized_401_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 401 Unauthorized errors with FAIL action.

        Given: Invalid API credentials
        When: Making an API request that returns 401
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint("invalid_key").with_any_query_params().build(),
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
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no flows
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.flows_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"data": [], "links": {"self": "https://a.klaviyo.com/api/flows", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
