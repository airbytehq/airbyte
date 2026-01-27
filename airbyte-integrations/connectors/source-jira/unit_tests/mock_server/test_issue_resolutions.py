# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_resolutions"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueResolutionsStream(TestCase):
    """
    Tests for the Jira 'issue_resolutions' stream.

    This is a full refresh stream with pagination.
    Endpoint: /rest/api/3/resolution/search
    Extract field: values
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        resolution_records = [
            {
                "id": "1",
                "name": "Fixed",
                "description": "A fix for this issue is checked into the tree and tested.",
                "self": f"https://{_DOMAIN}/rest/api/3/resolution/1",
                "isDefault": False,
            },
            {
                "id": "2",
                "name": "Won't Fix",
                "description": "The problem described is an issue which will never be fixed.",
                "self": f"https://{_DOMAIN}/rest/api/3/resolution/2",
                "isDefault": False,
            },
            {
                "id": "3",
                "name": "Done",
                "description": "Work has been completed on this issue.",
                "self": f"https://{_DOMAIN}/rest/api/3/resolution/3",
                "isDefault": True,
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_resolutions_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(resolution_records)
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        resolution_ids = [r.record.data["id"] for r in output.records]
        assert "1" in resolution_ids
        assert "2" in resolution_ids
        assert "3" in resolution_ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly with multiple pages.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1
        page1_resolutions = [
            {"id": "1", "name": "Fixed", "self": f"https://{_DOMAIN}/rest/api/3/resolution/1"},
            {"id": "2", "name": "Won't Fix", "self": f"https://{_DOMAIN}/rest/api/3/resolution/2"},
        ]

        # Page 2
        page2_resolutions = [
            {"id": "3", "name": "Done", "self": f"https://{_DOMAIN}/rest/api/3/resolution/3"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_resolutions_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_resolutions)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_resolutions)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        resolution_ids = [r.record.data["id"] for r in output.records]
        assert "1" in resolution_ids
        assert "2" in resolution_ids
        assert "3" in resolution_ids

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_resolutions_endpoint(_DOMAIN).with_any_query_params().build(),
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
