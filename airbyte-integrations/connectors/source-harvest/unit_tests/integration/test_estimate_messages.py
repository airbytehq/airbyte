# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
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


_STREAM_NAME = "estimate_messages"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


def _create_parent_estimate(estimate_id: int = 1) -> Dict[str, Any]:
    """Helper function to create a parent estimate record."""
    return {
        "id": estimate_id,
        "client_id": 1,
        "number": "EST-001",
        "amount": 5000.0,
        "state": "sent",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


class TestEstimateMessagesStream(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        """
        Test full_refresh sync for estimate_messages stream with multiple parent estimates.
        This is a substream of estimates, so we need to mock both parent and child streams.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent estimates stream with 2 estimates
        parent_estimate_1 = _create_parent_estimate(estimate_id=1)
        parent_estimate_2 = _create_parent_estimate(estimate_id=2)
        parent_estimate_2["number"] = "EST-002"
        parent_estimate_2["amount"] = 7500.0

        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "estimates": [parent_estimate_1, parent_estimate_2],
                        "per_page": 50,
                        "total_pages": 1,
                        "total_entries": 2,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        # Mock estimate_messages substream for estimate_id=1
        with open(get_resource_path("http/response/estimate_messages.json")) as f:
            response_data_estimate1 = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.estimate_messages_endpoint(_ACCOUNT_ID, _API_TOKEN, estimate_id=1)
            .with_per_page(50)
            .with_query_param("updated_since", "2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(response_data_estimate1), status_code=200),
        )

        # Mock estimate_messages substream for estimate_id=2
        response_data_estimate2 = {
            "estimate_messages": [
                {
                    "id": 112,
                    "sent_by": "John Doe",
                    "sent_by_email": "john@example.com",
                    "sent_from": "Jane Manager",
                    "sent_from_email": "jane@example.com",
                    "recipients": [{"name": "Client B", "email": "clientb@example.com"}],
                    "subject": "Estimate EST-002",
                    "body": "Please review the second estimate",
                    "send_me_a_copy": True,
                    "event_type": "send",
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                }
            ],
            "per_page": 50,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
            "links": {},
        }

        http_mocker.get(
            HarvestRequestBuilder.estimate_messages_endpoint(_ACCOUNT_ID, _API_TOKEN, estimate_id=2)
            .with_per_page(50)
            .with_query_param("updated_since", "2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(response_data_estimate2), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve estimate_messages records from both estimates
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 111
        assert output.records[1].record.data["id"] == 112
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: Transformation should add parent_id field to records
        for record in output.records:
            assert "parent_id" in record.record.data, "Transformation should add 'parent_id' field to record"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test handling of empty results when an estimate has no messages.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent estimates stream
        parent_estimate = _create_parent_estimate(estimate_id=1)
        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"estimates": [parent_estimate], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}
                ),
                status_code=200,
            ),
        )

        # Mock empty estimate_messages response
        http_mocker.get(
            HarvestRequestBuilder.estimate_messages_endpoint(_ACCOUNT_ID, _API_TOKEN, estimate_id=1)
            .with_per_page(50)
            .with_query_param("updated_since", "2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({"estimate_messages": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
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

        # Mock parent estimates stream
        parent_estimate = {
            "id": 1,
            "client_id": 1,
            "number": "EST-001",
            "amount": 5000.0,
            "state": "draft",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"estimates": [parent_estimate], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}
                ),
                status_code=200,
            ),
        )

        # Mock estimate_messages substream
        from airbyte_cdk.test.mock_http import HttpRequest

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/estimates/1/messages",
                query_params={"per_page": "50", "updated_since": "2024-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "estimate_messages": [{"id": 9001, "created_at": "2024-01-02T10:00:00Z", "updated_at": "2024-01-02T10:00:00Z"}],
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
        # Substreams have nested state structure
        assert latest_state.__dict__["state"]["updated_at"] == "2024-01-02T10:00:00Z"

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        # Mock parent estimates stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, "invalid_token")
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

        # Mock parent estimates stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, _API_TOKEN)
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

        # Mock parent estimates stream with not found error
        http_mocker.get(
            HarvestRequestBuilder.estimates_endpoint(_ACCOUNT_ID, _API_TOKEN)
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
