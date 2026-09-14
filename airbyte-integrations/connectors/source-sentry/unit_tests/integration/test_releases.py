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
_STREAM_NAME = "releases"
_ORGANIZATION = "test-org"
_PROJECT = "test-project"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestReleasesStream(TestCase):
    """Tests for releases stream"""

    def _config(self) -> dict:
        return ConfigBuilder().build()

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test full refresh for releases stream"""
        http_mocker.get(
            SentryRequestBuilder.releases_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            create_response("releases", has_next=False),
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        assert len(output.records) >= 1, f"Expected release records"
        assert output.records[0].record.data["version"] == "1.0.0"

    @HttpMocker()
    def test_pagination(self, http_mocker: HttpMocker):
        """Test pagination for releases"""
        http_mocker.get(
            SentryRequestBuilder.releases_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            [create_response("releases", has_next=True, cursor="next"), create_response("releases", has_next=False)],
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # Assert on count
        assert len(output.records) == 2, f"Expected 2 releases from 2 pages"

        # Assert on actual data values
        assert output.records[0].record.data["id"] == "release123"
        assert output.records[0].record.data["version"] == "1.0.0"
        assert output.records[1].record.data["id"] == "release123"
        assert output.records[1].record.data["version"] == "1.0.0"

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with previous state for releases stream.

        Releases is a data feed stream (is_data_feed: true). This test validates:
        - Connector accepts state from previous sync
        - Records from API are emitted (no client-side filtering)
        - State is updated to latest record's dateCreated

        NOTE: Releases stream does NOT have record_filter configured in manifest,
        so all records from API response are emitted. We use state earlier than
        the record dates to simulate records being "new" relative to state.
        """
        # ARRANGE - Previous state from last sync (2024-01-01, earlier than records)
        previous_state_date = "2024-01-01T08:00:00.000000Z"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"dateCreated": previous_state_date}).build()

        # Mock returns releases (dateCreated = 2024-01-10, after state 01-01)
        # Releases stream lacks record_filter, so all records are emitted
        http_mocker.get(
            SentryRequestBuilder.releases_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            create_response("releases", has_next=False),
        )

        # ACT - Pass state to get_source() for proper state management
        source = get_source(config=self._config(), state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog, state=state)

        # ASSERT - Records returned
        assert len(output.records) >= 1, f"Expected at least 1 record, got {len(output.records)}"

        # ASSERT - Verify record content
        record = output.records[0].record.data
        assert record["id"] == "release123", f"Expected release123, got {record['id']}"
        assert record["version"] == "1.0.0", f"Expected version 1.0.0, got {record['version']}"
        assert record["dateCreated"] == "2024-01-10T08:00:00Z", f"Expected dateCreated 2024-01-10, got {record['dateCreated']}"

        # ASSERT - State message with latest dateCreated
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        new_state = output.most_recent_state.stream_state.__dict__
        # State should be updated to the latest record (01-10)
        assert new_state["dateCreated"].startswith("2024-01-10T08:00:00"), f"Expected state to advance to latest record, got {new_state}"

    @HttpMocker()
    def test_incremental_sync_first_sync_emits_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state for releases stream.

        This tests:
        - Connector works in incremental mode without existing state (first sync)
        - Records are returned using default behavior (no start time filtering)
        - State message is emitted with latest record's dateCreated
        """
        # ARRANGE - Mock API returns releases (no state, so uses default behavior)
        http_mocker.get(
            SentryRequestBuilder.releases_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            create_response("releases", has_next=False),
        )

        # ACT - First incremental sync (no state parameter)
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT - Records returned
        assert len(output.records) >= 1, f"Expected at least 1 release record, got {len(output.records)}"

        # ASSERT - Record values
        first_record = output.records[0].record.data
        assert first_record["id"] == "release123", f"Expected release123, got {first_record['id']}"
        assert first_record["version"] == "1.0.0", f"Expected version 1.0.0, got {first_record['version']}"
        assert first_record["dateCreated"] == "2024-01-10T08:00:00Z", f"Expected dateCreated timestamp, got {first_record['dateCreated']}"

        # ASSERT - State message emitted with cursor value (KEY VALIDATION)
        assert len(output.state_messages) > 0, "Expected state messages to be emitted on first sync"
        state = output.most_recent_state.stream_state.__dict__
        # State should be set to the latest record's dateCreated
        assert state["dateCreated"] is not None, "Expected state to have dateCreated cursor"
        assert state["dateCreated"].startswith(
            "2024-01-10T08:00:00"
        ), f"Expected state cursor to be latest record's dateCreated, got {state}"

    @HttpMocker()
    def test_incremental_pagination_with_data_feed(self, http_mocker: HttpMocker):
        """
        Test is_data_feed: When Page 1 has old records, don't fetch Page 2.

        Scenario for is_data_feed: true with data sorted newest→oldest:
        - State: Jan 16 (last sync ended here)
        - Page 1: [Jan 18 ✅, Jan 16 ⚠️, Jan 15 ❌] - Has old record (Jan 15)
        - Page 2: Exists (API says has_next=true) but all records would be old

        Expected behavior:
        1. Fetch Page 1 → Get 3 records [Jan 18, Jan 16, Jan 15]
        2. Emit ALL 3 records from Page 1 (no filtering!)
        3. Detect: Jan 15 <= state (Jan 16) → Reached boundary!
        4. STOP: Don't fetch Page 2 (would be all older than Jan 15)
        5. Result: 3 records, 1 API call (saves fetching Page 2) ✅

        This tests the is_data_feed pagination optimization.
        """
        # ARRANGE - State from previous sync (2024-01-16)
        previous_state_date = "2024-01-16T09:00:00.000000Z"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"dateCreated": previous_state_date}).build()

        # Mock API - Only Page 1 (is_data_feed prevents Page 2 fetch)
        # Page 1: Mixed dates [Jan 18, Jan 16, Jan 15]
        # The oldest record (Jan 15) is <= state (Jan 16) → boundary reached!
        #
        # NOTE: We set has_next=True (API says Page 2 exists)
        # But is_data_feed detects boundary and doesn't fetch Page 2!
        http_mocker.get(
            SentryRequestBuilder.releases_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            # Page 1: 3 records, has_next=True but pagination stops here!
            create_response("releases_mixed_dates", has_next=True, cursor="cursor123"),
        )

        # ACT
        source = get_source(config=self._config(), state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=self._config(), catalog=catalog, state=state)

        # ASSERT - is_data_feed: Only Page 1 fetched despite has_next=True
        assert len(output.records) == 3, f"Expected 3 records from Page 1 only, got {len(output.records)}"

        # Verify all 3 records from Page 1 (no filtering - emit all)
        assert output.records[0].record.data["id"] == "release789"
        assert output.records[0].record.data["dateCreated"] == "2024-01-18T14:00:00Z"  # New

        assert output.records[1].record.data["id"] == "release456"
        assert output.records[1].record.data["dateCreated"] == "2024-01-16T14:00:00Z"  # At state

        assert output.records[2].record.data["id"] == "release123"
        assert output.records[2].record.data["dateCreated"] == "2024-01-15T14:00:00Z"  # Old (boundary!)

        # KEY PROOF OF is_data_feed:
        # - We set has_next=True (API says Page 2 exists)
        # - Page 1 has Jan 15 <= state Jan 16 (boundary reached!)
        # - Connector made ONLY 1 API call (fetched Page 1 only)
        # - Page 2 was NOT fetched (is_data_feed worked!)
        #
        # This test proves: When Page 1 contains records older than state,
        # pagination stops even though API says more pages exist! ✅

        # ASSERT - State updated to latest record
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["dateCreated"].startswith("2024-01-18T14:00:00"), f"Expected state updated to latest, got {new_state}"
