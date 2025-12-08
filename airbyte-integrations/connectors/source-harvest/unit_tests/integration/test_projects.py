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
_STREAM_NAME = "projects"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectsStream(TestCase):
    """
    Tests for the Harvest 'projects' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Pagination is handled properly
    - Incremental sync with updated_since parameter
    - Projects with various configurations (billable, fixed fee, etc.)
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of projects.

        Given: A configured Harvest connector
        When: Running a full refresh sync for the projects stream
        Then: The connector should make the correct API request and return all records
        """
        # ARRANGE: Set up config
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock the API response
        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "projects": [
                            {
                                "id": 14307913,
                                "name": "Online Store - Phase 1",
                                "code": "OS1",
                                "is_active": True,
                                "is_billable": True,
                                "is_fixed_fee": False,
                                "bill_by": "Project",
                                "client_id": 5735776,
                                "starts_on": "2023-01-01",
                                "ends_on": None,
                                "budget": 5000.0,
                                "budget_by": "project",
                                "budget_is_monthly": False,
                                "notify_when_over_budget": True,
                                "over_budget_notification_percentage": 80.0,
                                "created_at": "2023-01-15T11:00:00Z",
                                "updated_at": "2023-06-20T15:00:00Z",
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
        assert record["id"] == 14307913
        assert record["name"] == "Online Store - Phase 1"
        assert record["code"] == "OS1"
        assert record["is_active"] is True
        assert record["is_billable"] is True
        assert record["client_id"] == 5735776

        # ASSERT: Should have stream status messages indicating successful sync
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        NOTE: This test validates pagination for the 'projects' stream, but since all 32 streams
        use the same DefaultPaginator configuration, this provides pagination coverage for all
        streams in the connector. See test_clients.py::test_pagination_multiple_pages for the
        complete list of covered streams.

        Given: An API that returns multiple pages of projects
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock first page with pagination
        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "projects": [
                            {
                                "id": 1001,
                                "name": "Project Alpha",
                                "code": "PA",
                                "is_active": True,
                                "is_billable": True,
                                "client_id": 101,
                                "created_at": "2023-01-01T00:00:00Z",
                                "updated_at": "2023-01-01T00:00:00Z",
                            },
                            {
                                "id": 1002,
                                "name": "Project Beta",
                                "code": "PB",
                                "is_active": True,
                                "is_billable": False,
                                "client_id": 102,
                                "created_at": "2023-01-02T00:00:00Z",
                                "updated_at": "2023-01-02T00:00:00Z",
                            },
                        ],
                        "per_page": 50,
                        "total_pages": 2,
                        "page": 1,
                        "links": {"next": "https://api.harvestapp.com/v2/projects?page=2&per_page=50"},
                    }
                ),
                status_code=200,
            ),
        )

        # ARRANGE: Mock second page (last page)
        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_page(2)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "projects": [
                            {
                                "id": 1003,
                                "name": "Project Gamma",
                                "code": "PG",
                                "is_active": False,
                                "is_billable": True,
                                "client_id": 103,
                                "created_at": "2023-01-03T00:00:00Z",
                                "updated_at": "2023-01-03T00:00:00Z",
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
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "projects": [
                            {
                                "id": 2001,
                                "name": "New Project Delta",
                                "code": "NPD",
                                "is_active": True,
                                "is_billable": True,
                                "client_id": 201,
                                "created_at": "2024-01-02T10:00:00Z",
                                "updated_at": "2024-01-02T10:00:00Z",
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
        assert output.records[0].record.data["name"] == "New Project Delta"

        # ASSERT: State should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["updated_at"] == "2024-01-02T10:00:00Z"
        ), "State should be updated to the updated_at timestamp of the latest record"

    @HttpMocker()
    def test_projects_with_various_configurations(self, http_mocker: HttpMocker):
        """
        Test that connector handles projects with different configurations.

        Given: Projects with various settings (fixed fee, hourly, with budgets)
        When: Running a full refresh sync
        Then: All project types should be correctly parsed
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock response with different project types
        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "projects": [
                            {
                                "id": 3001,
                                "name": "Fixed Fee Project",
                                "code": "FFP",
                                "is_active": True,
                                "is_billable": True,
                                "is_fixed_fee": True,
                                "bill_by": "Project",
                                "client_id": 301,
                                "fee": 10000.0,
                                "created_at": "2023-01-01T00:00:00Z",
                                "updated_at": "2023-01-01T00:00:00Z",
                            },
                            {
                                "id": 3002,
                                "name": "Hourly Project",
                                "code": "HP",
                                "is_active": True,
                                "is_billable": True,
                                "is_fixed_fee": False,
                                "bill_by": "Project",
                                "client_id": 302,
                                "hourly_rate": 150.0,
                                "budget": 5000.0,
                                "budget_by": "project",
                                "created_at": "2023-01-02T00:00:00Z",
                                "updated_at": "2023-01-02T00:00:00Z",
                            },
                            {
                                "id": 3003,
                                "name": "Non-Billable Internal",
                                "code": "NBI",
                                "is_active": True,
                                "is_billable": False,
                                "is_fixed_fee": False,
                                "bill_by": "none",
                                "client_id": None,
                                "created_at": "2023-01-03T00:00:00Z",
                                "updated_at": "2023-01-03T00:00:00Z",
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

        # ASSERT: Should retrieve all three project types with different configurations
        assert len(output.records) == 3

        # ASSERT: Fixed fee project should have correct structure
        fixed_fee_project = output.records[0].record.data
        assert fixed_fee_project["id"] == 3001
        assert fixed_fee_project["is_fixed_fee"] is True
        assert "fee" in fixed_fee_project

        # ASSERT: Hourly project should have rate and budget information
        hourly_project = output.records[1].record.data
        assert hourly_project["id"] == 3002
        assert hourly_project["is_fixed_fee"] is False
        assert "hourly_rate" in hourly_project
        assert "budget" in hourly_project

        # ASSERT: Non-billable project should have correct billing configuration
        non_billable = output.records[2].record.data
        assert non_billable["id"] == 3003
        assert non_billable["is_billable"] is False

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no projects
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock empty response
        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"projects": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
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
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        http_mocker.get(
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, "invalid_token")
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
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
            HarvestRequestBuilder.projects_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
