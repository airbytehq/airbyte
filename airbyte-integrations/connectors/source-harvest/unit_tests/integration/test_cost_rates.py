# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict
from unittest import TestCase

from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_STREAM_NAME = "cost_rates"
_PARENT_STREAM_NAME = "users"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


def _create_parent_user(user_id: int = 1) -> Dict[str, Any]:
    """Helper function to create a parent user record."""
    return {
        "id": user_id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


class TestCostRatesStream(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        """
        Test full_refresh sync for cost_rates stream with multiple parent users.

        This is a substream of users, so we need to:
        1. Mock the parent users stream response with 2+ users
        2. Mock the cost_rates response for each user
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent users stream with 2 users
        parent_user_1 = _create_parent_user(user_id=1)
        parent_user_2 = _create_parent_user(user_id=2)
        parent_user_2["first_name"] = "Jane"
        parent_user_2["email"] = "jane@example.com"

        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"users": [parent_user_1, parent_user_2], "per_page": 50, "total_pages": 1, "total_entries": 2, "page": 1, "links": {}}
                ),
                status_code=200,
            ),
        )

        # Mock cost_rates substream for user_id=1
        with open(get_resource_path("http/response/cost_rates.json")) as f:
            response_data_user1 = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.cost_rates_endpoint(_ACCOUNT_ID, _API_TOKEN, user_id=1).with_per_page(50).build(),
            HttpResponse(body=json.dumps(response_data_user1), status_code=200),
        )

        # Mock cost_rates substream for user_id=2
        response_data_user2 = {
            "cost_rates": [
                {
                    "id": 12346,
                    "amount": 85.0,
                    "start_date": "2024-02-01",
                    "end_date": None,
                    "created_at": "2024-02-01T00:00:00Z",
                    "updated_at": "2024-02-01T00:00:00Z",
                }
            ],
            "per_page": 50,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
            "links": {},
        }

        http_mocker.get(
            HarvestRequestBuilder.cost_rates_endpoint(_ACCOUNT_ID, _API_TOKEN, user_id=2).with_per_page(50).build(),
            HttpResponse(body=json.dumps(response_data_user2), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve cost_rates records from both users
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 12345
        assert output.records[1].record.data["id"] == 12346

        # ASSERT: All records should belong to the correct stream
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: Transformation should add parent_id field to records
        for record in output.records:
            assert "parent_id" in record.record.data, "Transformation should add 'parent_id' field to record"

        # ASSERT: Should have expected cost rate data structure for both records
        cost_rate_1 = output.records[0].record.data
        assert cost_rate_1["amount"] == 75.0
        assert "start_date" in cost_rate_1

        cost_rate_2 = output.records[1].record.data
        assert cost_rate_2["amount"] == 85.0
        assert "start_date" in cost_rate_2

    @HttpMocker()
    def test_incremental_sync(self, http_mocker: HttpMocker) -> None:
        """
        Test incremental sync for cost_rates stream.

        Cost rates supports incremental sync using updated_at cursor.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent users stream
        parent_user = _create_parent_user(user_id=1)
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"users": [parent_user], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        # Mock cost_rates with incremental sync
        with open(get_resource_path("http/response/cost_rates.json")) as f:
            response_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.cost_rates_endpoint(_ACCOUNT_ID, _API_TOKEN, user_id=1).with_per_page(50).build(),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2024-01-01T00:00:00Z"}).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # ASSERT: Should retrieve records updated after the cursor timestamp
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 12345
        assert output.records[0].record.data["updated_at"] == "2024-01-01T00:00:00Z"

        # ASSERT: All records should belong to the correct stream
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: State should be updated
        # Note: cost_rates is a substream that relies on parent (users) stream state
        # and doesn't emit its own cursor state, so we only verify state messages exist
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test handling of empty results when a user has no cost rates.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent users stream
        parent_user = _create_parent_user(user_id=1)
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"users": [parent_user], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        # Mock empty cost_rates response
        http_mocker.get(
            HarvestRequestBuilder.cost_rates_endpoint(_ACCOUNT_ID, _API_TOKEN, user_id=1).with_per_page(50).build(),
            HttpResponse(
                body=json.dumps({"cost_rates": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: No records but no errors
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        # Mock parent users stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, "invalid_token")
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

        # Mock parent users stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
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

        # Mock parent users stream with not found error
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
