#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .response_builder import EmptyResponseBuilder


_STREAM_NAME = "segments"
_BASE_URL = "https://api.sendgrid.com"


def _get_response(filename: str) -> str:
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / filename
    return response_path.read_text()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


@freezegun.freeze_time("2024-01-15T00:00:00Z")
class TestSegmentsStream:
    """Tests for the segments stream (simple, no pagination, field_path: [results])."""

    def test_read_full_refresh(self):
        """Test basic full refresh sync."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(url=f"{_BASE_URL}/v3/marketing/segments/2.0"),
                HttpResponse(body=_get_response("segments.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 1
            assert actual_messages.records[0].record.data["id"] == "seg-123-abc"
            assert actual_messages.records[0].record.data["name"] == "Active Users"

    def test_read_returns_expected_fields(self):
        """Test that all expected fields are present in the response."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(url=f"{_BASE_URL}/v3/marketing/segments/2.0"),
                HttpResponse(body=_get_response("segments.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            record_data = actual_messages.records[0].record.data
            assert "id" in record_data
            assert "name" in record_data
            assert "contacts_count" in record_data
            assert "created_at" in record_data
            assert "updated_at" in record_data

    def test_read_empty_results_no_errors(self):
        """Test that empty results don't produce errors in logs."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(url=f"{_BASE_URL}/v3/marketing/segments/2.0"),
                EmptyResponseBuilder(is_array=False, records_path="results").build(),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 0
            assert len(actual_messages.errors) == 0
            for log in actual_messages.logs:
                assert "error" not in log.log.message.lower()
