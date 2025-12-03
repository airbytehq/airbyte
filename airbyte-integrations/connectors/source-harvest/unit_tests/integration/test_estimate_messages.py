# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict
from unittest import TestCase

from unit_tests.conftest import get_source, get_resource_path
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
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
        "updated_at": "2024-01-01T00:00:00Z"
    }


class TestEstimateMessagesStream(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        """
        Test full_refresh sync for estimate_messages stream.
        This is a substream of estimates, so we need to mock both.
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
                body=json.dumps({
                    "estimates": [parent_estimate],
                    "per_page": 50,
                    "total_pages": 1,
                    "total_entries": 1,
                    "page": 1,
                    "links": {}
                }),
                status_code=200
            )
        )

        # Mock estimate_messages substream
        with open(get_resource_path("http/response/estimate_messages.json")) as f:
            response_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.estimate_messages_endpoint(_ACCOUNT_ID, _API_TOKEN, estimate_id=1)
            .with_per_page(50)
            .with_query_param("updated_since", "2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(response_data), status_code=200)
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve all estimate_messages records
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 111
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

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
                body=json.dumps({
                    "estimates": [parent_estimate],
                    "per_page": 50,
                    "total_pages": 1,
                    "total_entries": 1,
                    "page": 1,
                    "links": {}
                }),
                status_code=200
            )
        )

        # Mock empty estimate_messages response
        http_mocker.get(
            HarvestRequestBuilder.estimate_messages_endpoint(_ACCOUNT_ID, _API_TOKEN, estimate_id=1)
            .with_per_page(50)
            .with_query_param("updated_since", "2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps({
                    "estimate_messages": [],
                    "per_page": 50,
                    "total_pages": 0,
                    "total_entries": 0,
                    "page": 1,
                    "links": {}
                }),
                status_code=200
            )
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should handle empty results gracefully with no records
        assert len(output.records) == 0
