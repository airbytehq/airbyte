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
_STREAM_NAME = "contacts"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestContactsStream(TestCase):
    """Tests for the Harvest 'contacts' stream."""

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test that connector correctly fetches contacts."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        with open(get_resource_path("http/response/contacts.json")) as f:
            response_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve exactly one contact record with correct data
        assert len(output.records) == 1
        assert output.records[0].record.data["first_name"] == "Jane"
        assert output.records[0].record.data["last_name"] == "Doe"

        # ASSERT: Record should belong to the correct stream
        assert output.records[0].record.stream == _STREAM_NAME

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock empty response
        http_mocker.get(
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"contacts": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
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

        http_mocker.get(
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, "invalid_token")
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
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, _API_TOKEN)
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

        http_mocker.get(
            HarvestRequestBuilder.contacts_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "contacts": [{"id": 9001, "created_at": "2024-01-02T10:00:00Z", "updated_at": "2024-01-02T10:00:00Z"}],
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

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 9001
        assert output.records[0].record.data["updated_at"] == "2024-01-02T10:00:00Z"
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert latest_state.__dict__["updated_at"] == "2024-01-02T10:00:00Z"
