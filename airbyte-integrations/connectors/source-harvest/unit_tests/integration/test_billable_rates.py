# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from typing import Any, Dict
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "billable_rates"
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


@freezegun.freeze_time(_NOW.isoformat())
class TestBillableRatesStream(TestCase):
    """Tests for the Harvest 'billable_rates' stream."""

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test that connector correctly fetches billable_rates from multiple parent users.

        This is a substream of users, so we need to:
        1. Mock the parent users stream response with 2+ users
        2. Mock the billable_rates response for each user
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

        # Mock billable_rates substream for user_id=1
        with open(get_resource_path("http/response/billable_rates.json")) as f:
            response_data_user1 = json.load(f)

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/users/1/billable_rates",
                query_params={"per_page": "50"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data_user1), status_code=200),
        )

        # Mock billable_rates substream for user_id=2
        response_data_user2 = {
            "billable_rates": [
                {
                    "id": 67891,
                    "amount": 150.0,
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
            HttpRequest(
                url="https://api.harvestapp.com/v2/users/2/billable_rates",
                query_params={"per_page": "50"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data_user2), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve billable_rates records from both users
        assert len(output.records) >= 2

        # ASSERT: All records should belong to the correct stream
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: Transformation should add parent_id field to records
        for record in output.records:
            assert "parent_id" in record.record.data, "Transformation should add 'parent_id' field to record"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test handling of empty results when a users has no billable_rates.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock the parent users stream
        with open(get_resource_path("http/response/users.json")) as f:
            parent_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(parent_data), status_code=200),
        )

        # Mock empty billable_rates substream response
        from airbyte_cdk.test.mock_http import HttpRequest

        parent_id = parent_data["users"][0]["id"]
        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/users/{parent_id}/billable_rates",
                query_params={"per_page": "50"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(
                body=json.dumps({"billable_rates": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
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
