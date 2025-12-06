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
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder


_STREAM_NAME = "blocks"
_BASE_URL = "https://api.sendgrid.com"


def _get_response(filename: str) -> str:
    """Load a JSON response template from the resource directory."""
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / filename
    return response_path.read_text()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


@freezegun.freeze_time("2024-01-15T00:00:00Z")
class TestBlocksStream:
    """Tests for the blocks stream with offset pagination and incremental sync."""

    def test_read_full_refresh_single_page(self):
        """Test basic full refresh sync with a single page of results."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/blocks",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("blocks.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 1
            assert actual_messages.records[0].record.data["email"] == "blocked@example.com"

    def test_read_full_refresh_with_pagination(self):
        """Test full refresh sync with multiple pages using offset pagination."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            # First page - return 500 records to trigger pagination
            first_page_records = json.loads(_get_response("blocks.json")) * 500
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/blocks",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=json.dumps(first_page_records), status_code=200),
            )

            # Second page - return fewer records to stop pagination
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/blocks",
                    query_params={
                        "limit": "500",
                        "offset": "500",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("blocks.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 501

    def test_read_incremental_emits_state(self):
        """Test incremental sync emits correct stream state message."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/blocks",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("blocks.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(
                source,
                config=config,
                catalog=_create_catalog(sync_mode=SyncMode.incremental),
            )

            assert len(actual_messages.records) == 1
            assert len(actual_messages.state_messages) > 0
