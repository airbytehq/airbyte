# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase
import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker

# Import builders
from integration.config import ConfigBuilder
from integration.request_builder import SentryRequestBuilder
from integration.response_builder import create_response, error_response

# Import conftest helper
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import get_source

# Test constants
_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "events"
_ORGANIZATION = "test-org"
_PROJECT = "test-project"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestEventsStream(TestCase):
    """Comprehensive tests for events stream"""

    def _config(self) -> dict:
        """Helper to create config using builder"""
        return ConfigBuilder().with_organization(_ORGANIZATION).with_project(_PROJECT).with_auth_token(_AUTH_TOKEN).build()

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of events.

        This tests:
        - Correct URL is called
        - Auth header is set properly
        - Response is parsed correctly
        """
        # ARRANGE
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            create_response("events", has_next=False)
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT
        assert len(output.records) == 2, f"Expected 2 records, got {len(output.records)}"

        # Verify first record
        record = output.records[0].record.data
        assert record["id"] == "abc123def456"
        assert record["platform"] == "javascript"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.
        """
        # ARRANGE: Mock returns two responses sequentially
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            [
                create_response("events", has_next=True, cursor="page2"),
                create_response("events", has_next=False, cursor="page2")
            ]
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        # ASSERT
        assert len(output.records) == 4, f"Expected 4 records from 2 pages, got {len(output.records)}"

    @HttpMocker()
    def test_authentication_error_401(self, http_mocker: HttpMocker):
        """
        Test that connector handles 401 authentication errors appropriately.
        """
        # ARRANGE
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            error_response(401)
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog, expecting_exception=True)

        # ASSERT
        assert len(output.records) == 0, f"Expected 0 records on auth failure, got {len(output.records)}"

    @HttpMocker()
    def test_rate_limit_error_429(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit errors.
        """
        # ARRANGE
        http_mocker.get(
            SentryRequestBuilder.events_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            error_response(429)
        )

        # ACT
        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog, expecting_exception=True)

        # ASSERT
        assert len(output.records) == 0, f"Expected 0 records on rate limit, got {len(output.records)}"
