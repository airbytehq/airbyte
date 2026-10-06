#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .response_builder import EmptyResponseBuilder


_STREAM_NAME = "stats_automations"
_BASE_URL = "https://api.sendgrid.com"


def _get_response(filename: str) -> str:
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / filename
    return response_path.read_text()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


@freezegun.freeze_time("2024-01-15T00:00:00Z")
class TestStatsAutomationsStream:
    """
    Tests for the stats_automations stream with cursor-based pagination.
    This stream uses the same paginator as singlesend_stats.
    """

    def test_read_full_refresh_single_page(self):
        """Test basic full refresh sync with a single page of results."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/marketing/stats/automations",
                    query_params={"page_size": "50"},
                ),
                HttpResponse(body=_get_response("stats_automations.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 1
            assert actual_messages.records[0].record.data["id"] == "auto-123-abc"
            assert actual_messages.records[0].record.data["aggregation"] == "total"
            assert actual_messages.records[0].record.data["step_id"] == "step-1"
            assert "stats" in actual_messages.records[0].record.data

    def test_read_full_refresh_with_pagination(self):
        """Test full refresh sync with multiple pages using cursor pagination."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            first_page_response = {
                "results": [
                    {
                        "id": "auto-1",
                        "aggregation": "total",
                        "step_id": "step-1",
                        "stats": {
                            "bounces": 3,
                            "clicks": 100,
                            "delivered": 500,
                            "opens": 250,
                            "requests": 510,
                        },
                    }
                ],
                "_metadata": {"next": "https://api.sendgrid.com/v3/marketing/stats/automations?page_token=token123&page_size=50"},
            }
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/marketing/stats/automations",
                    query_params={"page_size": "50"},
                ),
                HttpResponse(body=json.dumps(first_page_response), status_code=200),
            )

            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/marketing/stats/automations?page_token=token123&page_size=50",
                ),
                HttpResponse(body=_get_response("stats_automations.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 2
            assert actual_messages.records[0].record.data["id"] == "auto-1"
            assert actual_messages.records[1].record.data["id"] == "auto-123-abc"

    def test_read_returns_expected_fields(self):
        """Test that all expected fields are present in the response."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/marketing/stats/automations",
                    query_params={"page_size": "50"},
                ),
                HttpResponse(body=_get_response("stats_automations.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            record_data = actual_messages.records[0].record.data
            assert "id" in record_data
            assert "aggregation" in record_data
            assert "step_id" in record_data
            assert "stats" in record_data
            stats = record_data["stats"]
            assert "bounces" in stats
            assert "clicks" in stats
            assert "delivered" in stats
            assert "opens" in stats

    def test_read_empty_results_no_errors(self):
        """Test that empty results don't produce errors in logs."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/marketing/stats/automations",
                    query_params={"page_size": "50"},
                ),
                EmptyResponseBuilder(is_array=False, records_path="results").build(),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 0
            assert len(actual_messages.errors) == 0
            for log in actual_messages.logs:
                assert "error" not in log.log.message.lower()
