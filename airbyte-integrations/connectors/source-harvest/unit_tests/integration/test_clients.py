import json
from datetime import datetime, timezone
from unittest import TestCase
import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from unit_tests.conftest import get_source
from integration.config import (ConfigBuilder)
from integration.request_builder import HarvestRequestBuilder

_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "clients"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"

@freezegun.freeze_time(_NOW.isoformat())
class TestClientsStream(TestCase):
    """
    Tests for the Harvest 'clients' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Pagination is handled properly
    - Incremental sync with updated_since parameter
    - Error handling for various HTTP status codes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of clients.

        Given: A configured Harvest connector
        When: Running a full refresh sync for the clients stream
        Then: The connector should make the correct API request and return all records
        """
        # ARRANGE: Set up config
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock the API response
        # Note: The clients stream has incremental_sync configured, so it always sends updated_since
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({
                    "clients": [
                        {
                            "id": 101,
                            "name": "Acme Corporation",
                            "is_active": True,
                            "currency": "USD",
                            "address": "123 Main St",
                            "created_at": "2023-01-15T10:00:00Z",
                            "updated_at": "2023-06-20T15:30:00Z"
                        }
                    ],
                    "per_page": 50,
                    "total_pages": 1,
                    "total_entries": 1,
                    "page": 1,
                    "links": {
                        "first": "https://api.harvestapp.com/v2/clients?page=1&per_page=50",
                        "last": "https://api.harvestapp.com/v2/clients?page=1&per_page=50",
                        "previous": None,
                        "next": None
                    }
                }),
                status_code=200
            )
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Verify results
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 101
        assert record["name"] == "Acme Corporation"
        assert record["is_active"] is True
        assert record["currency"] == "USD"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of clients
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock first page with pagination
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({
                    "clients": [
                        {"id": 101, "name": "Client 1", "is_active": True, "currency": "USD", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"},
                        {"id": 102, "name": "Client 2", "is_active": True, "currency": "EUR", "created_at": "2023-01-02T00:00:00Z", "updated_at": "2023-01-02T00:00:00Z"}
                    ],
                    "per_page": 50,
                    "total_pages": 2,
                    "page": 1,
                    "links": {
                        "first": "https://api.harvestapp.com/v2/clients?page=1&per_page=50",
                        "next": "https://api.harvestapp.com/v2/clients?page=2&per_page=50",
                        "last": "https://api.harvestapp.com/v2/clients?page=2&per_page=50"
                    }
                }),
                status_code=200
            )
        )

        # ARRANGE: Mock second page (last page)
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_page(2)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({
                    "clients": [
                        {"id": 103, "name": "Client 3", "is_active": False, "currency": "GBP", "created_at": "2023-01-03T00:00:00Z", "updated_at": "2023-01-03T00:00:00Z"}
                    ],
                    "per_page": 50,
                    "total_pages": 2,
                    "page": 2,
                    "links": {
                        "first": "https://api.harvestapp.com/v2/clients?page=1&per_page=50",
                        "previous": "https://api.harvestapp.com/v2/clients?page=1&per_page=50",
                        "last": "https://api.harvestapp.com/v2/clients?page=2&per_page=50"
                    }
                }),
                status_code=200
            )
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should have records from both pages
        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == 101
        assert output.records[1].record.data["id"] == 102
        assert output.records[2].record.data["id"] == 103

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
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_updated_since("2024-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({
                    "clients": [
                        {
                            "id": 201,
                            "name": "New Client Corp",
                            "is_active": True,
                            "currency": "USD",
                            "created_at": "2024-01-02T10:00:00Z",
                            "updated_at": "2024-01-02T10:00:00Z"
                        }
                    ],
                    "per_page": 50,
                    "total_pages": 1,
                    "page": 1,
                    "links": {}
                }),
                status_code=200
            )
        )

        # ACT: Run incremental sync
        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # ASSERT: Should return only records updated since last sync
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 201
        assert output.records[0].record.data["name"] == "New Client Corp"

        # ASSERT: State should be updated
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no clients
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock empty response
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({
                    "clients": [],
                    "per_page": 50,
                    "total_pages": 0,
                    "total_entries": 0,
                    "page": 1,
                    "links": {}
                }),
                status_code=200
            )
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: No records but no errors
        assert len(output.records) == 0

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 401 authentication errors appropriately.

        Given: Invalid API credentials
        When: Making an API request
        Then: The connector should handle the 401 error gracefully
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        # ARRANGE: Mock 401 Unauthorized response
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, "invalid_token")
                .with_per_page(50)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            HttpResponse(
                body=json.dumps({"error": "invalid_token", "error_description": "The access token is invalid"}),
                status_code=401
            )
        )

        # ACT: Run the connector (expecting it to handle error)
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        # ASSERT: No records due to auth failure
        assert len(output.records) == 0

    @HttpMocker()
    def test_rate_limit_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # ARRANGE: Mock 429 rate limit response
        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
                .with_per_page(50)
                .with_updated_since("2021-01-01T00:00:00Z")
                .build(),
            [
                HttpResponse(
                    body=json.dumps({"error": "rate_limit_exceeded"}),
                    status_code=429,
                    headers={"Retry-After": "1"}
                ),
                HttpResponse(
                    body=json.dumps({
                        "clients": [{"id": 101, "name": "Client 1", "is_active": True, "currency": "USD", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {}
                    }),
                    status_code=200
                )
            ]
        )

        # ACT: Run the connector
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should eventually succeed and return records
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 101
