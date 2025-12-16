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
_STREAM_NAME = "dashboards"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestDashboardsStream(TestCase):
    """
    Tests for the Jira 'dashboards' stream.

    This stream uses the standard paginator with 'dashboards' as the extract field.
    Endpoint: /rest/api/3/dashboard
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches dashboards with a single page.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        dashboard_records = [
            {
                "id": "10001",
                "name": "System Dashboard",
                "description": "Default system dashboard",
                "isFavourite": True,
                "self": f"https://{_DOMAIN}/rest/api/3/dashboard/10001",
            },
            {
                "id": "10002",
                "name": "Project Dashboard",
                "description": "Project overview dashboard",
                "isFavourite": False,
                "self": f"https://{_DOMAIN}/rest/api/3/dashboard/10002",
            },
        ]

        # First request doesn't include startAt parameter
        http_mocker.get(
            JiraRequestBuilder.dashboards_endpoint(_DOMAIN).with_max_results(50).build(),
            JiraPaginatedResponseBuilder("dashboards")
            .with_records(dashboard_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["name"] == "System Dashboard"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[1].record.data["name"] == "Project Dashboard"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles pagination across multiple pages.

        NOTE: This test validates pagination for the 'dashboards' stream, but many streams
        use the same DefaultPaginator configuration (startAt/maxResults with CursorPagination),
        so this provides pagination coverage for: boards, board_issues, dashboards, filters,
        groups, issue_changelogs, issue_comments, issue_field_configurations,
        issue_notification_schemes, issue_priorities, issue_resolutions, issue_type_schemes,
        issue_type_screen_schemes, issue_worklogs, labels, project_components, project_versions,
        projects, screen_schemes, screens, sprints, workflows, workflow_schemes

        Pagination stop_condition from manifest:
        {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}

        To exercise 2 pages:
        - Page 1: startAt=0, maxResults=2, total=3 -> 0 + 2 >= 3 is false, fetch page 2
        - Page 2: startAt=2, maxResults=2, total=3, isLast=true -> stops
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_records = [
            {"id": "10001", "name": "Dashboard 1"},
            {"id": "10002", "name": "Dashboard 2"},
        ]
        page2_records = [
            {"id": "10003", "name": "Dashboard 3"},
        ]

        # Page 1 request (first request doesn't include startAt)
        http_mocker.get(
            JiraRequestBuilder.dashboards_endpoint(_DOMAIN).with_max_results(50).build(),
            JiraPaginatedResponseBuilder("dashboards")
            .with_records(page1_records)
            .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
            .build(),
        )

        # Page 2 request (subsequent requests include startAt)
        http_mocker.get(
            JiraRequestBuilder.dashboards_endpoint(_DOMAIN).with_max_results(50).with_start_at(2).build(),
            JiraPaginatedResponseBuilder("dashboards")
            .with_records(page2_records)
            .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[2].record.data["id"] == "10003"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # First request doesn't include startAt parameter
        http_mocker.get(
            JiraRequestBuilder.dashboards_endpoint(_DOMAIN).with_max_results(50).build(),
            JiraPaginatedResponseBuilder("dashboards")
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
        Test that connector ignores 400 errors per the default error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # First request doesn't include startAt parameter
        http_mocker.get(
            JiraRequestBuilder.dashboards_endpoint(_DOMAIN).with_max_results(50).build(),
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
