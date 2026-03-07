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
from mock_server.response_builder import JiraAgileResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "boards"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestBoardsStream(TestCase):
    """
    Tests for the Jira 'boards' stream.

    This stream uses the Agile API v1 with 'values' as the extract field.
    Endpoint: /rest/agile/1.0/board
    Has record_filter: filters by config['projects'] if specified
    Has transformations: AddFields for projectId and projectKey
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches boards with a single page.
        Also verifies that transformations (AddFields) are applied.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        board_records = [
            {
                "id": 1,
                "name": "Scrum Board",
                "type": "scrum",
                "self": f"https://{_DOMAIN}/rest/agile/1.0/board/1",
                "location": {
                    "projectId": 10001,
                    "projectKey": "PROJ1",
                    "displayName": "Project One",
                    "projectName": "Project One",
                    "projectTypeKey": "software",
                },
            },
            {
                "id": 2,
                "name": "Kanban Board",
                "type": "kanban",
                "self": f"https://{_DOMAIN}/rest/agile/1.0/board/2",
                "location": {
                    "projectId": 10002,
                    "projectKey": "PROJ2",
                    "displayName": "Project Two",
                    "projectName": "Project Two",
                    "projectTypeKey": "software",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        # Verify basic fields
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["name"] == "Scrum Board"
        # Verify transformations (AddFields) are applied
        assert output.records[0].record.data["projectId"] == "10001"
        assert output.records[0].record.data["projectKey"] == "PROJ1"
        assert output.records[1].record.data["id"] == 2
        assert output.records[1].record.data["projectId"] == "10002"
        assert output.records[1].record.data["projectKey"] == "PROJ2"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles pagination across multiple pages.

        Pagination stop_condition from manifest:
        {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_records = [
            {"id": 1, "name": "Board 1", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
            {"id": 2, "name": "Board 2", "type": "kanban", "location": {"projectId": 10002, "projectKey": "PROJ2"}},
        ]
        page2_records = [
            {"id": 3, "name": "Board 3", "type": "scrum", "location": {"projectId": 10003, "projectKey": "PROJ3"}},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraAgileResponseBuilder("values")
                .with_records(page1_records)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraAgileResponseBuilder("values")
                .with_records(page2_records)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == 1
        assert output.records[1].record.data["id"] == 2
        assert output.records[2].record.data["id"] == 3

    @HttpMocker()
    def test_project_filter_config(self, http_mocker: HttpMocker):
        """
        Test that connector filters boards based on config['projects'] setting.

        The record_filter in manifest:
        {{ not config.get('projects') or record.get('location', {}).get('projectKey') in config['projects'] }}

        When projects config is set, only boards belonging to matching projects should be returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_projects(["PROJ1"]).build()

        board_records = [
            {"id": 1, "name": "Board 1", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
            {"id": 2, "name": "Board 2", "type": "kanban", "location": {"projectId": 10002, "projectKey": "PROJ2"}},
            {"id": 3, "name": "Board 3", "type": "scrum", "location": {"projectId": 10003, "projectKey": "PROJ3"}},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board_records)
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Only boards from PROJ1 should be returned due to the filter
        assert len(output.records) == 1
        assert output.records[0].record.data["projectKey"] == "PROJ1"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values").with_records([]).with_pagination(start_at=0, max_results=50, total=0, is_last=True).build(),
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
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
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
