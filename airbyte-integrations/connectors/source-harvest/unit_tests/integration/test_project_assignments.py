# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "project_assignments"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectAssignmentsStream(TestCase):
    """Tests for the Harvest 'project_assignments' stream."""

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test that connector correctly fetches project_assignments.

        Note: project_assignments is a substream of users, so we need to mock both.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock the parent users stream first
        with open(get_resource_path("http/response/users.json")) as f:
            users_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(users_data), status_code=200),
        )

        # Mock the project_assignments substream for the user
        with open(get_resource_path("http/response/project_assignments.json")) as f:
            response_data = json.load(f)

        # The path will be /users/{user_id}/project_assignments
        from airbyte_cdk.test.mock_http import HttpRequest

        user_id = users_data["users"][0]["id"]
        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/users/{user_id}/project_assignments",
                query_params={"per_page": "50", "updated_since": "2021-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1
        assert output.records[0].record.stream == _STREAM_NAME

        # ASSERT: Transformation should add parent_id field to records
        for record in output.records:
            assert "parent_id" in record.record.data, "Transformation should add 'parent_id' field to record"

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
        log_messages = [log.log.message for log in output.logs]
        assert any("Please ensure your credentials are valid" in msg for msg in log_messages)

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with state."""
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc))
            .build()
        )
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2024-01-01T00:00:00Z"}).build()

        # Mock parent users stream
        parent_user = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"users": [parent_user], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        # Mock project_assignments substream
        from airbyte_cdk.test.mock_http import HttpRequest

        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/users/1/project_assignments",
                query_params={"per_page": "50", "updated_since": "2024-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "project_assignments": [{"id": 9001, "created_at": "2024-01-02T10:00:00Z", "updated_at": "2024-01-02T10:00:00Z"}],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {},
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
