# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import SentryRequestBuilder
from integration.response_builder import create_response


# Test constants
_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "events"
_ORGANIZATION = "test-org"
_PROJECT = "test-project"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestEventsStream(TestCase):
    """Comprehensive tests for events stream"""

    def _config(self) -> dict:
        """Helper to create config using builder"""
        return ConfigBuilder().with_organization(_ORGANIZATION).with_project(_PROJECT).with_auth_token(_AUTH_TOKEN).build()

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of events.

        This tests:
        - Correct URL is called
        - Auth header is set properly
        - Query parameters (full=true, start, end) are passed correctly
        - Response is parsed correctly
        """
        # ARRANGE
        # Validate query params including full=true (from manifest) and start/end (from sync logic)
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN)
            .with_query_params(
                {
                    "full": "true",  # From manifest request_parameters
                    "start": "1900-01-01T00:00:00.000000Z",  # Default start for full_refresh
                    "end": _NOW.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # Current time (frozen)
                }
            )
            .build(),
            create_response("events", has_next=False),
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT
        assert len(output.records) == 2, f"Expected 2 records, got {len(output.records)}"

        # Verify first record
        record = output.records[0].record.data
        assert record["id"] == "abc123def456"
        assert record["platform"] == "javascript"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.
        """
        # ARRANGE: Mock page 1 (no cursor)
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN)
            .with_query_params({"full": "true", "start": "1900-01-01T00:00:00.000000Z", "end": _NOW.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})
            .build(),
            create_response("events", has_next=True, cursor="page2"),
        )

        # ARRANGE: Mock page 2 (with cursor)
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN)
            .with_query_params(
                {
                    "full": "true",
                    "cursor": "page2",  # Second request includes cursor!
                    "start": "1900-01-01T00:00:00.000000Z",
                    "end": _NOW.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
            .build(),
            create_response("events", has_next=False, cursor="page2"),
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT
        assert len(output.records) == 4, f"Expected 4 records from 2 pages, got {len(output.records)}"

        # Verify data from first page
        assert output.records[0].record.data["id"] == "abc123def456"
        assert output.records[0].record.data["platform"] == "javascript"
        # Verify data from second page
        assert output.records[2].record.data["id"] == "abc123def456"
        assert output.records[2].record.data["platform"] == "javascript"

    @HttpMocker()
    def test_incremental_sync_first_sync_emits_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state.

        This tests:
        - Connector uses default start date (1900-01-01) when no state exists
        - Query parameters (full=true, start, end) are passed correctly
        - State message is emitted with latest record's dateCreated
        """
        # ARRANGE
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN)
            .with_query_params(
                {
                    "full": "true",
                    "start": "1900-01-01T00:00:00.000000Z",  # Default start for first incremental sync
                    "end": _NOW.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
            .build(),
            create_response("events", has_next=False),
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT - Records
        assert len(output.records) == 2, f"Expected 2 records, got {len(output.records)}"

        # ASSERT - First record values
        first_record = output.records[0].record.data
        assert first_record["id"] == "abc123def456", f"Expected first record id, got {first_record['id']}"
        assert first_record["dateCreated"] == "2024-01-15T10:00:00Z", f"Expected first record date, got {first_record['dateCreated']}"
        assert first_record["platform"] == "javascript", f"Expected javascript platform, got {first_record['platform']}"

        # ASSERT - Second record values (latest)
        second_record = output.records[1].record.data
        assert second_record["id"] == "xyz789ghi012", f"Expected second record id, got {second_record['id']}"
        assert second_record["dateCreated"] == "2024-01-16T12:30:00Z", f"Expected second record date, got {second_record['dateCreated']}"
        assert second_record["platform"] == "python", f"Expected python platform, got {second_record['platform']}"

        # ASSERT - State message with latest dateCreated
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        state = output.most_recent_state.stream_state.__dict__
        # State format has microseconds, record doesn't - just verify it starts with the date
        assert state["dateCreated"].startswith("2024-01-16T12:30:00"), f"Expected state cursor to be latest record date, got {state}"

    @HttpMocker()
    def test_incremental_sync_with_state_uses_state_as_start(self, http_mocker: HttpMocker):
        """
        Test incremental sync with previous state.

        This tests:
        - Connector uses state cursor as start date in API request (API-side filtering!)
        - URL params include start=<state_date> (not default 1900-01-01)
        - Only records after the state date are returned
        - New state message is emitted with latest record's dateCreated
        """
        # ARRANGE - Previous state from last sync (2024-01-15)
        previous_state_date = "2024-01-15T10:00:00.000000Z"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"dateCreated": previous_state_date}).build()

        # Mock API call - EXPLICITLY validate that start param uses state date!
        # This proves Events stream does API-side filtering by passing state as start param
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN)
            .with_query_params(
                {
                    "full": "true",
                    "start": previous_state_date,  # ← VERIFY state is used as start param!
                    "end": _NOW.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
            .build(),
            # Return only 1 record (01-16 event, which is after state date 01-15)
            create_response("events_incremental", has_next=False),
        )

        # ACT - Pass state to get_source() for proper state management
        source = get_source(config=self._config(), state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog, state=state)

        # ASSERT - Records (only 1 record after state date)
        assert len(output.records) == 1, f"Expected 1 record after state date, got {len(output.records)}"

        # ASSERT - Record values (verify we got the 01-16 event)
        record = output.records[0].record.data
        assert record["id"] == "xyz789ghi012", f"Expected specific record id, got {record['id']}"
        assert record["dateCreated"] == "2024-01-16T12:30:00Z", f"Expected record after state date, got {record['dateCreated']}"
        assert record["platform"] == "python", f"Expected python platform, got {record['platform']}"

        # ASSERT - State message with latest dateCreated
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        new_state = output.most_recent_state.stream_state.__dict__
        # New state should be 01-16 (advanced from input state 01-15)
        assert new_state["dateCreated"].startswith(
            "2024-01-16T12:30:00"
        ), f"Expected state to advance to latest record date, got {new_state}"
