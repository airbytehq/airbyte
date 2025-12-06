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


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "projects"
_ORGANIZATION = "test-org"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectsStream(TestCase):
    """Tests for projects stream"""

    def _config(self) -> dict:
        return ConfigBuilder().build()

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test full refresh for projects stream"""
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(), create_response("projects", has_next=False)
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        assert len(output.records) >= 1, f"Expected project records"
        assert output.records[0].record.data["slug"] == "test-project"

    @HttpMocker()
    def test_pagination(self, http_mocker: HttpMocker):
        """Test pagination for projects stream"""
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(),
            [create_response("projects", has_next=True, cursor="next"), create_response("projects", has_next=False)],
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT - 2 records from 2 pages
        assert len(output.records) == 2, f"Expected 2 projects from 2 pages, got {len(output.records)}"

        # ASSERT - Verify record values
        assert output.records[0].record.data["id"] == "proj123"
        assert output.records[0].record.data["slug"] == "test-project"
        assert output.records[1].record.data["id"] == "proj123"
        assert output.records[1].record.data["slug"] == "test-project"

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with previous state for projects stream.

        Projects is a data feed stream (is_data_feed: true). This test validates:
        1. We pass state: "dateCreated = 2024-01-15"
        2. API returns ALL 3 records (2 old + 1 new) - no API-side filtering
        3. Connector applies record_filter to filter out old records
        4. Only 1 new record (after state date) should be emitted
        5. State is updated to latest record's dateCreated

        This tests EXPECTED BEHAVIOR (proper data feed filtering).
        If this test FAILS with 3 records instead of 1, it means record_filter is broken.
        """
        # ARRANGE - Previous state from last sync (2024-01-15)
        previous_state_date = "2024-01-15T00:00:00.000000Z"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"dateCreated": previous_state_date}).build()

        # Mock API returns ALL 3 projects (simulates real data feed behavior)
        # The API doesn't filter, so it returns everything:
        # projects_mixed_dates.json contains:
        #   - proj001: dateCreated = 2024-01-10 (BEFORE state, should be filtered out)
        #   - proj002: dateCreated = 2024-01-12 (BEFORE state, should be filtered out)
        #   - proj456: dateCreated = 2024-01-20 (AFTER state, should be kept)
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(),
            create_response("projects_mixed_dates", has_next=False),
        )

        # ACT - Run the sync with state
        # Connector should:
        # 1. Receive 3 records from API
        # 2. Apply record_filter: {{ record['dateCreated'] > stream_interval.start_time }}
        # 3. Filter out proj001 and proj002 (before state date)
        # 4. Emit only proj456 (after state date)
        source = get_source(config=self._config(), state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog, state=state)

        # ASSERT - EXPECTED: Only 1 record emitted (after client-side filtering)
        # If this fails with 3 records, it means record_filter is not working
        assert len(output.records) == 1, (
            f"Expected 1 record after filtering (API sent 3, connector should filter 2 old ones), "
            f"got {len(output.records)} records. "
            f"If you got 3 records, it means record_filter is broken."
        )

        # ASSERT - Verify it's the correct record (the only one after state date)
        record = output.records[0].record.data
        assert record["id"] == "proj456", f"Expected proj456 (the only project after state date), got {record['id']}"
        assert record["slug"] == "new-project", f"Expected new-project, got {record['slug']}"
        assert record["dateCreated"] == "2024-01-20T10:00:00Z", (
            f"Expected proj456 with date 2024-01-20 (after state 2024-01-15), " f"got {record['dateCreated']}"
        )

        # ASSERT - Verify old records were NOT emitted
        record_ids = [r.record.data["id"] for r in output.records]
        assert "proj001" not in record_ids, "proj001 should have been filtered out (dateCreated 2024-01-10 < state 2024-01-15)"
        assert "proj002" not in record_ids, "proj002 should have been filtered out (dateCreated 2024-01-12 < state 2024-01-15)"

        # ASSERT - State message with latest dateCreated
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        new_state = output.most_recent_state.stream_state.__dict__
        # State should be updated to the latest record (01-20)
        assert new_state["dateCreated"].startswith(
            "2024-01-20T10:00:00"
        ), f"Expected state to advance to latest record (2024-01-20), got {new_state}"

    @HttpMocker()
    def test_incremental_sync_first_sync_emits_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state for projects stream.

        This tests:
        - Connector works in incremental mode without existing state (first sync)
        - Records are returned using default behavior (no start time filtering)
        - State message is emitted with latest record's dateCreated
        """
        # ARRANGE - Mock API returns projects (no state, so uses default behavior)
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(), create_response("projects", has_next=False)
        )

        # ACT - First incremental sync (no state parameter)
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT - Records returned
        assert len(output.records) >= 1, f"Expected at least 1 project record, got {len(output.records)}"

        # ASSERT - Record values
        first_record = output.records[0].record.data
        assert first_record["id"] == "proj123", f"Expected proj123, got {first_record['id']}"
        assert first_record["slug"] == "test-project", f"Expected test-project, got {first_record['slug']}"
        assert first_record["dateCreated"] == "2023-01-01T00:00:00Z", f"Expected dateCreated timestamp, got {first_record['dateCreated']}"

        # ASSERT - State message emitted with cursor value (KEY VALIDATION)
        assert len(output.state_messages) > 0, "Expected state messages to be emitted on first sync"
        state = output.most_recent_state.stream_state.__dict__
        # State should be set to the latest record's dateCreated
        assert state["dateCreated"] is not None, "Expected state to have dateCreated cursor"
        assert state["dateCreated"].startswith(
            "2023-01-01T00:00:00"
        ), f"Expected state cursor to be latest record's dateCreated, got {state}"
