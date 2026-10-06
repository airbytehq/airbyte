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
_STREAM_NAME = "segments"
_API_KEY = "test_api_key_abc123"


def _segment_record(segment_id: str, name: str, updated: str, created: str = "2024-01-01T10:00:00+00:00", is_active: bool = True):
    return {
        "type": "segment",
        "id": segment_id,
        "attributes": {
            "name": name,
            "definition": {
                "condition_groups": [
                    {
                        "conditions": [
                            {
                                "type": "profile-group-membership",
                                "is_member": True,
                                "group_ids": ["group_abc"],
                            }
                        ]
                    }
                ]
            },
            "created": created,
            "updated": updated,
            "is_active": is_active,
            "is_processing": False,
            "is_starred": False,
        },
        "links": {"self": f"https://a.klaviyo.com/api/segments/{segment_id}"},
        "relationships": {
            "profiles": {
                "links": {
                    "self": f"https://a.klaviyo.com/api/segments/{segment_id}/relationships/profiles",
                    "related": f"https://a.klaviyo.com/api/segments/{segment_id}/profiles",
                }
            },
            "tags": {
                "data": [],
                "links": {
                    "self": f"https://a.klaviyo.com/api/segments/{segment_id}/relationships/tags",
                    "related": f"https://a.klaviyo.com/api/segments/{segment_id}/tags",
                },
            },
            "flow-triggers": {
                "data": [],
                "links": {
                    "self": f"https://a.klaviyo.com/api/segments/{segment_id}/relationships/flow-triggers",
                    "related": f"https://a.klaviyo.com/api/segments/{segment_id}/flow-triggers",
                },
            },
        },
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestSegmentsStream(TestCase):
    """
    Tests for the Klaviyo 'segments' stream.

    Stream configuration from manifest.yaml:
    - Client-side incremental sync (is_client_side_incremental: true)
    - DatetimeBasedCursor on 'updated' field
    - Pagination: CursorPagination via links.next
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Transformations: AddFields to extract 'updated' from attributes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Given: A configured Klaviyo connector
        When: Running a full refresh sync for the segments stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [_segment_record("segment_001", "Repeat Purchasers", "2024-05-31T12:30:00+00:00")],
                        "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
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
        assert record["id"] == "segment_001"
        assert record["attributes"]["name"] == "Repeat Purchasers"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Given: An API that returns multiple pages of segments
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            [
                KlaviyoPaginatedResponseBuilder()
                .with_records([_segment_record("segment_001", "Segment 1", "2024-05-31T10:00:00+00:00")])
                .with_next_page_link("https://a.klaviyo.com/api/segments?page[cursor]=abc123")
                .build(),
                KlaviyoPaginatedResponseBuilder()
                .with_records([_segment_record("segment_002", "Segment 2", "2024-05-31T11:00:00+00:00")])
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "segment_001"
        assert output.records[1].record.data["id"] == "segment_002"

    @HttpMocker()
    def test_client_side_incremental_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should fetch all records and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [_segment_record("segment_001", "Test Segment", "2024-05-31T12:30:00+00:00")],
                        "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "segment_001"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        assert "updated" in latest_state

    @HttpMocker()
    def test_client_side_incremental_with_prior_state(self, http_mocker: HttpMocker):
        """
        For client-side incremental streams (is_client_side_incremental: true), the connector
        fetches all records from the API but filters them client-side based on the state.

        Given: A previous sync state with an updated cursor value
        When: Running an incremental sync
        Then: The connector should filter records client-side and only return new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-03-01T00:00:00+0000"}).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            _segment_record("segment_old", "Old Segment", "2024-02-15T10:00:00+00:00"),
                            _segment_record("segment_new", "New Segment", "2024-03-15T10:00:00+00:00", created="2024-03-10T10:00:00+00:00"),
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "segment_new"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        assert latest_state["updated"] == "2024-03-15T10:00:00+0000"

    @HttpMocker()
    def test_data_feed_stops_pagination_on_old_records(self, http_mocker: HttpMocker):
        """
        Given: A state with a cursor value and API returning old records
        When: Running an incremental sync
        Then: The connector should stop pagination when old records are detected
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-03-01T00:00:00+0000"}).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [_segment_record("segment_old", "Old Segment", "2024-02-01T10:00:00+00:00")],
                        "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 0

    @HttpMocker()
    def test_transformation_adds_updated_field(self, http_mocker: HttpMocker):
        """
        Given: A segment record with updated in attributes
        When: Running a sync
        Then: The 'updated' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [_segment_record("segment_transform", "Transform Test", "2024-05-31T14:45:00+00:00")],
                        "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
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
        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            [
                HttpResponse(
                    body=json.dumps({"errors": [{"detail": "Rate limit exceeded"}]}),
                    status_code=429,
                    headers={"Retry-After": "1"},
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [_segment_record("segment_after_retry", "After Retry", "2024-05-31T10:00:00+00:00")],
                            "links": {"self": "https://a.klaviyo.com/api/segments", "next": None},
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
        assert output.records[0].record.data["id"] == "segment_after_retry"

        log_messages = [log.log.message for log in output.logs]
        assert any(
            "Backing off" in msg and "UserDefinedBackoffException" in msg and "429" in msg for msg in log_messages
        ), "Expected backoff log message for 429 rate limit"
        assert any(
            "Sleeping for" in msg and "seconds" in msg for msg in log_messages
        ), "Expected retry sleeping log message for 429 rate limit"

    @HttpMocker()
    def test_unauthorized_401_error_fails(self, http_mocker: HttpMocker):
        """
        Given: Invalid API credentials
        When: Making an API request that returns 401
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint("invalid_key").build(),
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
        Given: API credentials with insufficient permissions
        When: Making an API request that returns 403
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
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
        Given: An API that returns no segments
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.segments_endpoint(_API_KEY).build(),
            HttpResponse(
                body=json.dumps({"data": [], "links": {"self": "https://a.klaviyo.com/api/segments", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
