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
_STREAM_NAME = "projects"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectsStream(TestCase):
    """
    Tests for the Jira 'projects' stream.

    This stream uses the standard paginator with 'values' as the extract field.
    Endpoint: /rest/api/3/project/search
    Request parameters: expand=description,lead, status=['live', 'archived', 'deleted']
    Has record_filter: filters by config['projects'] if specified
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches projects with a single page.

        The projects stream sends static request parameters from manifest.yaml:
        - expand=description,lead (to include project description and lead info)
        - status=['live', 'archived', 'deleted'] (to include all project statuses)

        Note: Using with_any_query_params() because the CDK's HttpRequest matcher
        requires exact parameter matching, and the status parameter encoding varies.
        The filters stream uses explicit expand validation as a reference for static params.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        project_records = [
            {
                "id": "10001",
                "key": "PROJ1",
                "name": "Project One",
                "description": "First project",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10001",
            },
            {
                "id": "10002",
                "key": "PROJ2",
                "name": "Project Two",
                "description": "Second project",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10002",
            },
        ]

        # Projects endpoint uses static expand and status parameters from manifest.yaml.
        # Using with_any_query_params() because the status parameter has complex encoding.
        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(project_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["key"] == "PROJ1"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[1].record.data["key"] == "PROJ2"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles pagination across multiple pages.

        Pagination stop_condition from manifest:
        {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}

        To exercise 2 pages:
        - Page 1: startAt=0, maxResults=2, total=3 -> 0 + 2 >= 3 is false, fetch page 2
        - Page 2: startAt=2, maxResults=2, total=3, isLast=true -> stops
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_records = [
            {"id": "10001", "key": "PROJ1", "name": "Project 1"},
            {"id": "10002", "key": "PROJ2", "name": "Project 2"},
        ]
        page2_records = [
            {"id": "10003", "key": "PROJ3", "name": "Project 3"},
        ]

        # Page 1 request
        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
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
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[2].record.data["id"] == "10003"

    @HttpMocker()
    def test_project_filter_config(self, http_mocker: HttpMocker):
        """
        Test that connector filters projects based on config['projects'] setting.

        The record_filter in manifest:
        {{ not config.get('projects') or record.get('key') in config['projects'] }}

        When projects config is set, only matching projects should be returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_projects(["PROJ1"]).build()

        project_records = [
            {"id": "10001", "key": "PROJ1", "name": "Project One"},
            {"id": "10002", "key": "PROJ2", "name": "Project Two"},
            {"id": "10003", "key": "PROJ3", "name": "Project Three"},
        ]

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(project_records)
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Only PROJ1 should be returned due to the filter
        assert len(output.records) == 1
        assert output.records[0].record.data["key"] == "PROJ1"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
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
        Test that connector ignores 400 errors per the default error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
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
