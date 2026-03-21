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
_STREAM_NAME = "screen_tab_fields"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestScreenTabFieldsStream(TestCase):
    """
    Tests for the Jira 'screen_tab_fields' stream.

    This is a nested substream that depends on screen_tabs (which depends on screens).
    Endpoint: /rest/api/3/screens/{screenId}/tabs/{tabId}/fields
    Primary key: id
    Uses selector_base (root array response)
    Transformations: AddFields (tabId, screenId)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_tabs(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with fields from multiple tabs across screens.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock screens endpoint (grandparent stream)
        screens = [
            {"id": 10000, "name": "Screen 1"},
            {"id": 10001, "name": "Screen 2"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screens)
            .with_pagination(start_at=0, max_results=100, total=2, is_last=True)
            .build(),
        )

        # Mock screen tabs for screen 1
        screen1_tabs = [
            {"id": 10100, "name": "Tab 1"},
        ]

        # Mock screen tabs for screen 2
        screen2_tabs = [
            {"id": 10200, "name": "Tab A"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps(screen1_tabs), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "10001").build(),
            HttpResponse(body=json.dumps(screen2_tabs), status_code=200),
        )

        # Mock screen tab fields for screen 1, tab 1
        tab1_fields = [
            {"id": "field1", "name": "Summary"},
            {"id": "field2", "name": "Description"},
        ]

        # Mock screen tab fields for screen 2, tab A
        tabA_fields = [
            {"id": "field3", "name": "Priority"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_tab_fields_endpoint(_DOMAIN, "10000", "10100").build(),
            HttpResponse(body=json.dumps(tab1_fields), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.screen_tab_fields_endpoint(_DOMAIN, "10001", "10200").build(),
            HttpResponse(body=json.dumps(tabA_fields), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        field_ids = [r.record.data["id"] for r in output.records]
        assert "field1" in field_ids
        assert "field2" in field_ids
        assert "field3" in field_ids

    @HttpMocker()
    def test_transformations(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds tabId and screenId.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        screens = [
            {"id": 10000, "name": "Screen 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screens)
            .with_pagination(start_at=0, max_results=100, total=1, is_last=True)
            .build(),
        )

        screen_tabs = [
            {"id": 10100, "name": "Tab 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps(screen_tabs), status_code=200),
        )

        tab_fields = [
            {"id": "field1", "name": "Summary"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_tab_fields_endpoint(_DOMAIN, "10000", "10100").build(),
            HttpResponse(body=json.dumps(tab_fields), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "field1"
        assert record["tabId"] == 10100
        assert record["screenId"] == 10000

    @HttpMocker()
    def test_empty_screens(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty screens gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([])
            .with_pagination(start_at=0, max_results=100, total=0, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_tab_with_no_fields(self, http_mocker: HttpMocker):
        """
        Test that connector handles tabs with no fields gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        screens = [
            {"id": 10000, "name": "Screen 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screens_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screens)
            .with_pagination(start_at=0, max_results=100, total=1, is_last=True)
            .build(),
        )

        screen_tabs = [
            {"id": 10100, "name": "Tab 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_tabs_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps(screen_tabs), status_code=200),
        )

        http_mocker.get(
            JiraRequestBuilder.screen_tab_fields_endpoint(_DOMAIN, "10000", "10100").build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
