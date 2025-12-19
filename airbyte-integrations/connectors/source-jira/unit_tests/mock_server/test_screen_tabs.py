# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "screen_tabs"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestScreenTabsStream(TestCase):
    """
    Tests for the Jira 'screen_tabs' stream.

    This is a substream of screens.
    Endpoint: /rest/api/3/screens/{screen_id}/tabs
    Uses SubstreamPartitionRouter with screens as parent
    Has transformation: AddFields for screenId
    Error handler: 400 errors are IGNORED
    """

    @HttpMocker()
    def test_full_refresh_with_parent_screens(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches screen tabs from multiple parent screens.

        Per playbook: "All substreams should be tested against at least two parent records"
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent screens endpoint
        screen_records = [
            {"id": 1, "name": "Screen 1", "description": "First screen"},
            {"id": 2, "name": "Screen 2", "description": "Second screen"},
        ]
        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screen_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock screen tabs for screen 1
        screen1_tabs = [
            {"id": 101, "name": "Tab 1"},
            {"id": 102, "name": "Tab 2"},
        ]
        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "1").build(),
            HttpResponse(body=json.dumps(screen1_tabs), status_code=200),
        )

        # Mock screen tabs for screen 2
        screen2_tabs = [
            {"id": 201, "name": "Tab A"},
        ]
        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "2").build(),
            HttpResponse(body=json.dumps(screen2_tabs), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        # Verify transformation: screenId should be added
        screen_ids = [r.record.data.get("screenId") for r in output.records]
        assert 1 in screen_ids
        assert 2 in screen_ids

    @HttpMocker()
    def test_empty_parent_screens(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent screens gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([])
            .with_pagination(start_at=0, max_results=50, total=0, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_screen_without_tabs(self, http_mocker: HttpMocker):
        """
        Test that connector handles screens without tabs.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent screens endpoint
        screen_records = [
            {"id": 1, "name": "Screen 1", "description": "First screen"},
        ]
        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screen_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock empty tabs for screen 1
        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "1").build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 400 errors per the error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent screens endpoint
        screen_records = [
            {"id": 1, "name": "Screen 1", "description": "First screen"},
        ]
        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screen_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock 400 error for screen tabs
        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "1").build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["Bad request"]}),
                status_code=400,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
