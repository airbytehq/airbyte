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
_STREAM_NAME = "issue_priorities"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssuePrioritiesStream(TestCase):
    """
    Tests for the Jira 'issue_priorities' stream.

    This is a full refresh stream with pagination.
    Endpoint: /rest/api/3/priority/search
    Extract field: values
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        priority_records = [
            {
                "id": "1",
                "name": "Highest",
                "description": "This problem will block progress.",
                "statusColor": "#d04437",
                "iconUrl": f"https://{_DOMAIN}/images/icons/priorities/highest.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/priority/1",
                "isDefault": False,
            },
            {
                "id": "2",
                "name": "High",
                "description": "Serious problem that could block progress.",
                "statusColor": "#f15C75",
                "iconUrl": f"https://{_DOMAIN}/images/icons/priorities/high.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/priority/2",
                "isDefault": False,
            },
            {
                "id": "3",
                "name": "Medium",
                "description": "Has the potential to affect progress.",
                "statusColor": "#f79232",
                "iconUrl": f"https://{_DOMAIN}/images/icons/priorities/medium.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/priority/3",
                "isDefault": True,
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_priorities_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(priority_records)
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        priority_ids = [r.record.data["id"] for r in output.records]
        assert "1" in priority_ids
        assert "2" in priority_ids
        assert "3" in priority_ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly with multiple pages.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1
        page1_priorities = [
            {"id": "1", "name": "Highest", "self": f"https://{_DOMAIN}/rest/api/3/priority/1"},
            {"id": "2", "name": "High", "self": f"https://{_DOMAIN}/rest/api/3/priority/2"},
        ]

        # Page 2
        page2_priorities = [
            {"id": "3", "name": "Medium", "self": f"https://{_DOMAIN}/rest/api/3/priority/3"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_priorities_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_priorities)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_priorities)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        priority_ids = [r.record.data["id"] for r in output.records]
        assert "1" in priority_ids
        assert "2" in priority_ids
        assert "3" in priority_ids

    @HttpMocker()
    def test_default_priority_property(self, http_mocker: HttpMocker):
        """
        Test that isDefault property is correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        priority_records = [
            {
                "id": "3",
                "name": "Medium",
                "isDefault": True,
                "self": f"https://{_DOMAIN}/rest/api/3/priority/3",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_priorities_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(priority_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["isDefault"] is True

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_priorities_endpoint(_DOMAIN).with_any_query_params().build(),
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
