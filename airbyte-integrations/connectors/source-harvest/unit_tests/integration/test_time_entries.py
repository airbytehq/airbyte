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
from integration.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "time_entries"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestTimeEntriesStream(TestCase):
    """
    Tests for the Harvest 'time_entries' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Pagination is handled properly
    - Incremental sync with updated_since parameter
    - Time entries with various configurations (billable, running, locked)
    - Error handling for various HTTP status codes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of time entries.

        Given: A configured Harvest connector
        When: Running a full refresh sync for the time_entries stream
        Then: The connector should make the correct API request and return all records
        """
        # ARRANGE: Set up config
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock the API response
        # Note: The time_entries stream has incremental_sync configured, so it always sends updated_since
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 636709355,
                                "spent_date": "2024-01-15",
                                "hours": 3.5,
                                "rounded_hours": 3.5,
                                "notes": "Worked on API integration",
                                "is_locked": False,
                                "is_closed": False,
                                "is_billed": False,
                                "is_running": False,
                                "billable": True,
                                "budgeted": True,
                                "billable_rate": 100.0,
                                "cost_rate": 50.0,
                                "created_at": "2024-01-15T12:30:00Z",
                                "updated_at": "2024-01-15T12:30:00Z",
                                "user": {"id": 1782884, "name": "John Doe"},
                                "client": {"id": 5735776, "name": "ABC Corp", "currency": "USD"},
                                "project": {"id": 14307913, "name": "Online Store - Phase 1", "code": "OS1"},
                                "task": {"id": 8083365, "name": "Development"},
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "total_entries": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve exactly one record with correct data
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 636709355
        assert record["hours"] == 3.5
        assert record["billable"] is True
        assert record["user"]["name"] == "John Doe"
        assert record["project"]["name"] == "Online Store - Phase 1"

        # ASSERT: Record should belong to the correct stream
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        NOTE: This test validates pagination for the 'time_entries' stream, but since all 32 streams
        use the same DefaultPaginator configuration, this provides pagination coverage for all
        streams in the connector. See test_clients.py::test_pagination_multiple_pages for the
        complete list of covered streams.

        Given: An API that returns multiple pages of time entries
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock first page with pagination
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 1001,
                                "spent_date": "2024-01-01",
                                "hours": 2.0,
                                "billable": True,
                                "is_running": False,
                                "created_at": "2024-01-01T10:00:00Z",
                                "updated_at": "2024-01-01T10:00:00Z",
                            },
                            {
                                "id": 1002,
                                "spent_date": "2024-01-02",
                                "hours": 4.5,
                                "billable": True,
                                "is_running": False,
                                "created_at": "2024-01-02T10:00:00Z",
                                "updated_at": "2024-01-02T10:00:00Z",
                            },
                        ],
                        "per_page": 50,
                        "total_pages": 2,
                        "page": 1,
                        "links": {"next": "https://api.harvestapp.com/v2/time_entries?page=2&per_page=50"},
                    }
                ),
                status_code=200,
            ),
        )

        # ARRANGE: Mock second page (last page)
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_page(2)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 1003,
                                "spent_date": "2024-01-03",
                                "hours": 8.0,
                                "billable": False,
                                "is_running": False,
                                "created_at": "2024-01-03T10:00:00Z",
                                "updated_at": "2024-01-03T10:00:00Z",
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 2,
                        "page": 2,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve records from both pages in correct order
        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == 1001
        assert output.records[1].record.data["id"] == 1002
        assert output.records[2].record.data["id"] == 1003

        # ASSERT: All records should belong to the correct stream
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test that incremental sync uses the updated_since parameter correctly.

        Given: A previous sync state with an updated_at cursor value
        When: Running an incremental sync
        Then: The connector should pass updated_since and only return new/updated records
        """
        last_sync_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).with_replication_start_date(last_sync_date).build()

        # Set up state from previous sync
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2024-01-01T00:00:00Z"}).build()

        # ARRANGE: Mock incremental request with updated_since parameter
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 2001,
                                "spent_date": "2024-01-02",
                                "hours": 5.5,
                                "billable": True,
                                "is_running": False,
                                "notes": "New time entry after last sync",
                                "created_at": "2024-01-02T14:00:00Z",
                                "updated_at": "2024-01-02T14:00:00Z",
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # ACT: Run incremental sync
        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # ASSERT: Should return only records updated since last sync
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 2001
        assert output.records[0].record.data["hours"] == 5.5

        # ASSERT: State should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["updated_at"] == "2024-01-02T14:00:00Z"
        ), "State should be updated to the updated_at timestamp of the latest record"

    @HttpMocker()
    def test_time_entries_with_various_states(self, http_mocker: HttpMocker):
        """
        Test that connector handles time entries with different states.

        Given: Time entries with various states (running, locked, billed, non-billable)
        When: Running a full refresh sync
        Then: All time entry types should be correctly parsed
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock response with different time entry states
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 3001,
                                "spent_date": "2024-01-15",
                                "hours": 2.0,
                                "billable": True,
                                "is_running": True,
                                "timer_started_at": "2024-01-15T09:00:00Z",
                                "is_locked": False,
                                "is_billed": False,
                                "notes": "Currently running timer",
                                "created_at": "2024-01-15T09:00:00Z",
                                "updated_at": "2024-01-15T11:00:00Z",
                            },
                            {
                                "id": 3002,
                                "spent_date": "2024-01-14",
                                "hours": 8.0,
                                "billable": True,
                                "is_running": False,
                                "is_locked": True,
                                "locked_reason": "Approved timesheet",
                                "is_billed": True,
                                "notes": "Locked and billed entry",
                                "created_at": "2024-01-14T09:00:00Z",
                                "updated_at": "2024-01-14T17:00:00Z",
                            },
                            {
                                "id": 3003,
                                "spent_date": "2024-01-13",
                                "hours": 3.5,
                                "billable": False,
                                "is_running": False,
                                "is_locked": False,
                                "is_billed": False,
                                "notes": "Non-billable internal work",
                                "created_at": "2024-01-13T09:00:00Z",
                                "updated_at": "2024-01-13T12:30:00Z",
                            },
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve all three time entry types with different states
        assert len(output.records) == 3

        # ASSERT: Running timer should have correct state and timer information
        running_entry = output.records[0].record.data
        assert running_entry["id"] == 3001
        assert running_entry["is_running"] is True
        assert "timer_started_at" in running_entry

        # ASSERT: Locked and billed entry should have correct status flags
        locked_entry = output.records[1].record.data
        assert locked_entry["id"] == 3002
        assert locked_entry["is_locked"] is True
        assert locked_entry["is_billed"] is True
        assert "locked_reason" in locked_entry

        # ASSERT: Non-billable entry should have correct billing configuration
        non_billable = output.records[2].record.data
        assert non_billable["id"] == 3003
        assert non_billable["billable"] is False

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no time entries
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock empty response
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"time_entries": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should return zero records without raising errors
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_time_entry_with_nested_objects(self, http_mocker: HttpMocker):
        """
        Test that connector correctly parses nested objects in time entries.

        Given: Time entries with full nested user, client, project, task data
        When: Running a full refresh sync
        Then: All nested objects should be correctly parsed
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock response with full nested data
        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "time_entries": [
                            {
                                "id": 4001,
                                "spent_date": "2024-01-15",
                                "hours": 6.0,
                                "billable": True,
                                "is_running": False,
                                "created_at": "2024-01-15T09:00:00Z",
                                "updated_at": "2024-01-15T15:00:00Z",
                                "user": {"id": 1782884, "name": "Jane Smith"},
                                "client": {"id": 5735776, "name": "Tech Startup Inc", "currency": "USD"},
                                "project": {"id": 14307913, "name": "Mobile App Development", "code": "MAD"},
                                "task": {"id": 8083365, "name": "Backend Development"},
                                "user_assignment": {"id": 130403296, "is_project_manager": True, "is_active": True, "hourly_rate": 150.0},
                                "task_assignment": {"id": 155505014, "billable": True, "is_active": True, "hourly_rate": 150.0},
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve exactly one record with complete nested data
        assert len(output.records) == 1
        record = output.records[0].record.data

        # ASSERT: Nested user object should be correctly parsed
        assert record["user"]["id"] == 1782884
        assert record["user"]["name"] == "Jane Smith"

        # ASSERT: Nested client object should contain all expected fields
        assert record["client"]["id"] == 5735776
        assert record["client"]["currency"] == "USD"

        # ASSERT: Nested project object should have project code
        assert record["project"]["code"] == "MAD"

        # ASSERT: Nested task object should have task name
        assert record["task"]["name"] == "Backend Development"

        # ASSERT: Nested assignment objects should contain rate information
        assert record["user_assignment"]["is_project_manager"] is True
        assert record["task_assignment"]["hourly_rate"] == 150.0

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, "invalid_token")
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "invalid_token"}), status_code=401),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_forbidden_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 403 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "forbidden"}), status_code=403),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_not_found_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 404 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            HarvestRequestBuilder.time_entries_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "not_found"}), status_code=404),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
