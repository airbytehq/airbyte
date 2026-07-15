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
_STREAM_NAME = "filters"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestFiltersStream(TestCase):
    """
    Tests for the Jira 'filters' stream.

    This is a full refresh stream with pagination.
    Endpoint: /rest/api/3/filter/search
    Uses retriever_use_cache for caching
    """

    # Static expand parameter from manifest.yaml for filters stream
    _FILTERS_EXPAND = "description,owner,jql,viewUrl,searchUrl,favourite,favouritedCount,sharePermissions,isWritable,subscriptions"

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches filters in a single page.

        This test validates that the filters stream sends the correct static request parameters:
        - expand parameter with all filter fields to include in the response
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        filter_records = [
            {
                "id": "10001",
                "name": "My Open Issues",
                "description": "All open issues assigned to me",
                "self": f"https://{_DOMAIN}/rest/api/3/filter/10001",
                "jql": "assignee = currentUser() AND resolution = Unresolved",
                "favourite": True,
            },
            {
                "id": "10002",
                "name": "All Project Issues",
                "description": "All issues in the project",
                "self": f"https://{_DOMAIN}/rest/api/3/filter/10002",
                "jql": "project = PROJ",
                "favourite": False,
            },
        ]

        # Filters endpoint uses static expand parameter from manifest.yaml
        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_max_results(50).with_expand(self._FILTERS_EXPAND).build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(filter_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["name"] == "My Open Issues"
        assert output.records[1].record.data["id"] == "10002"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles pagination across multiple pages.

        Pagination stop_condition: {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}
        Page 1: startAt=0, maxResults=2, total=3 -> 0 + 2 >= 3 is False, fetch page 2
        Page 2: startAt=2, maxResults=2, total=3, isLast=True -> stops
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_records = [
            {"id": "10001", "name": "Filter 1", "self": f"https://{_DOMAIN}/rest/api/3/filter/10001"},
            {"id": "10002", "name": "Filter 2", "self": f"https://{_DOMAIN}/rest/api/3/filter/10002"},
        ]
        page2_records = [
            {"id": "10003", "name": "Filter 3", "self": f"https://{_DOMAIN}/rest/api/3/filter/10003"},
        ]

        # Use with_any_query_params() here because pagination involves dynamic startAt
        # parameters that change between pages (startAt=0 for page 1, startAt=2 for page 2)
        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_records)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_records)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        filter_ids = [r.record.data["id"] for r in output.records]
        assert "10001" in filter_ids
        assert "10002" in filter_ids
        assert "10003" in filter_ids

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_max_results(50).with_expand(self._FILTERS_EXPAND).build(),
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
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 400 errors per the error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_max_results(50).with_expand(self._FILTERS_EXPAND).build(),
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
