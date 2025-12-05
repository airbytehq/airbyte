# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_STREAM_NAME = "estimate_item_categories"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


class TestEstimateItemCategoriesStream(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        """
        Test full_refresh sync for estimate_item_categories stream.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        with open(get_resource_path("http/response/estimate_item_categories.json")) as f:
            response_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve all estimate_item_categories records
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1

        # ASSERT: All records should belong to the correct stream
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: Should have expected category data structure
        category = output.records[0].record.data
        assert category["name"] == "Service"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test handling of empty results when no estimate item categories exist.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"estimate_item_categories": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}
                ),
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
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "estimate_item_categories": [
                            {"id": 9001, "created_at": "2024-01-02T10:00:00Z", "updated_at": "2024-01-02T10:00:00Z"}
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

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 9001
        assert output.records[0].record.data["updated_at"] == "2024-01-02T10:00:00Z"
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert latest_state.__dict__["updated_at"] == "2024-01-02T10:00:00Z"

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        http_mocker.get(
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, "invalid_token")
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
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
            HarvestRequestBuilder.estimate_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
