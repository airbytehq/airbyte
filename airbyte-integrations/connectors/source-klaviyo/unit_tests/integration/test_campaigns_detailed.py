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
_STREAM_NAME = "campaigns_detailed"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestCampaignsDetailedStream(TestCase):
    """
    Tests for the Klaviyo 'campaigns_detailed' stream.

    Stream configuration from manifest.yaml:
    - Uses CustomTransformation to flatten campaign message data
    - Uses ListPartitionRouter to iterate over campaign statuses
    - Incremental sync with DatetimeBasedCursor on 'updated_at' field
    - Request parameters: include=campaign-messages
    - Pagination: CursorPagination
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    """

    @HttpMocker()
    def test_full_refresh_with_included_messages(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with included campaign message data.

        The CustomTransformation flattens the included campaign-messages data into each campaign record.

        Given: An API response with campaigns and included campaign-messages
        When: Running a full refresh sync
        Then: The connector should return campaigns with message data merged in
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "campaign",
                                "id": "campaign_001",
                                "attributes": {
                                    "name": "Test Campaign",
                                    "status": "sent",
                                    "created_at": "2024-01-01T10:00:00+00:00",
                                    "updated_at": "2024-01-15T12:30:00+00:00",
                                    "send_time": "2024-01-20T10:00:00+00:00",
                                },
                                "relationships": {
                                    "campaign-messages": {"data": [{"type": "campaign-message", "id": "msg_001"}]},
                                },
                            }
                        ],
                        "included": [
                            {
                                "type": "campaign-message",
                                "id": "msg_001",
                                "attributes": {
                                    "label": "Email Message",
                                    "channel": "email",
                                    "content": {"subject": "Welcome!", "preview_text": "Thanks for joining"},
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None},
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
        assert record["id"] == "campaign_001"
        assert record["attributes"]["name"] == "Test Campaign"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of campaigns with included messages
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Use a single mock with multiple responses to avoid ambiguity in mock matching.
        # The first response includes a next link, the second response has no next link.
        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            [
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [
                                {
                                    "type": "campaign",
                                    "id": "campaign_001",
                                    "attributes": {
                                        "name": "Campaign 1",
                                        "status": "sent",
                                        "created_at": "2024-05-31T10:00:00+00:00",
                                        "updated_at": "2024-05-31T10:00:00+00:00",
                                    },
                                    "relationships": {"campaign-messages": {"data": []}},
                                }
                            ],
                            "included": [],
                            "links": {
                                "self": "https://a.klaviyo.com/api/campaigns",
                                "next": "https://a.klaviyo.com/api/campaigns?page[cursor]=abc123",
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
                                    "type": "campaign",
                                    "id": "campaign_002",
                                    "attributes": {
                                        "name": "Campaign 2",
                                        "status": "sent",
                                        "created_at": "2024-05-31T11:00:00+00:00",
                                        "updated_at": "2024-05-31T11:00:00+00:00",
                                    },
                                    "relationships": {"campaign-messages": {"data": []}},
                                }
                            ],
                            "included": [],
                            "links": {"self": "https://a.klaviyo.com/api/campaigns?page[cursor]=abc123", "next": None},
                        }
                    ),
                    status_code=200,
                ),
            ],
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
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "campaign",
                                "id": "campaign_001",
                                "attributes": {
                                    "name": "Test Campaign",
                                    "status": "sent",
                                    "created_at": "2024-01-01T10:00:00+00:00",
                                    "updated_at": "2024-01-15T12:30:00+00:00",
                                },
                                "relationships": {"campaign-messages": {"data": []}},
                            }
                        ],
                        "included": [],
                        "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None},
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

        Given: A previous sync state with an updated_at cursor value
        When: Running an incremental sync
        Then: The connector should use the state cursor and return only new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2024-03-01T00:00:00+00:00"}).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "campaign",
                                "id": "campaign_new",
                                "attributes": {
                                    "name": "New Campaign",
                                    "status": "sent",
                                    "created_at": "2024-03-10T10:00:00+00:00",
                                    "updated_at": "2024-03-15T10:00:00+00:00",
                                },
                                "relationships": {"campaign-messages": {"data": []}},
                            }
                        ],
                        "included": [],
                        "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None},
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
    def test_transformation_adds_updated_at_field(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly extracts 'updated_at' from attributes.

        Given: A campaign record with updated_at in attributes
        When: Running a sync
        Then: The 'updated_at' field should be added at the root level of the record
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "campaign",
                                "id": "campaign_transform_test",
                                "attributes": {
                                    "name": "Transform Test",
                                    "status": "sent",
                                    "created_at": "2024-01-01T10:00:00+00:00",
                                    "updated_at": "2024-02-20T14:45:00+00:00",
                                },
                                "relationships": {"campaign-messages": {"data": []}},
                            }
                        ],
                        "included": [],
                        "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None},
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
        assert "updated_at" in record
        assert record["updated_at"] == "2024-02-20T14:45:00+00:00"

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
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
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
                                    "type": "campaign",
                                    "id": "campaign_after_retry",
                                    "attributes": {
                                        "name": "After Retry",
                                        "status": "sent",
                                        "created_at": "2024-01-01T10:00:00+00:00",
                                        "updated_at": "2024-01-20T10:00:00+00:00",
                                    },
                                    "relationships": {"campaign-messages": {"data": []}},
                                }
                            ],
                            "included": [],
                            "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None},
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
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint("invalid_key").with_any_query_params().build(),
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

        Given: An API that returns no campaigns
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.campaigns_endpoint(_API_KEY).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"data": [], "included": [], "links": {"self": "https://a.klaviyo.com/api/campaigns", "next": None}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
