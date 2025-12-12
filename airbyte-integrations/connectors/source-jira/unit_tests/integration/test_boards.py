# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from integration.config import ConfigBuilder
from integration.request_builder import JiraRequestBuilder
from integration.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "boards"
_DOMAIN = "test.atlassian.net"
_EMAIL = "test@example.com"
_API_TOKEN = "test_api_token"


@freezegun.freeze_time(_NOW.isoformat())
class TestBoardsStream(TestCase):
    """
    Tests for the Jira 'boards' stream.

    The boards stream uses the Agile API (v1) and returns boards with pagination.
    It also applies a record_filter based on the projects config.
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of boards.

        Given: A configured Jira connector
        When: Running a full refresh sync for the boards stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(
                [
                    {
                        "id": 1,
                        "name": "Scrum Board",
                        "type": "scrum",
                        "location": {
                            "projectId": 10001,
                            "projectKey": "PROJ1",
                            "displayName": "Project One",
                        },
                    },
                    {
                        "id": 2,
                        "name": "Kanban Board",
                        "type": "kanban",
                        "location": {
                            "projectId": 10002,
                            "projectKey": "PROJ2",
                            "displayName": "Project Two",
                        },
                    },
                ]
            )
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["name"] == "Scrum Board"
        # Verify transformation adds projectId and projectKey fields
        assert output.records[0].record.data["projectId"] == "10001"
        assert output.records[0].record.data["projectKey"] == "PROJ1"
        assert output.records[1].record.data["id"] == 2
        assert output.records[1].record.data["name"] == "Kanban Board"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of boards
        When: Running a full refresh sync
        Then: The connector should follow pagination and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        # Use a list of responses to simulate pagination - responses are returned in order
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(
                    [
                        {"id": 1, "name": "Board 1", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
                        {"id": 2, "name": "Board 2", "type": "kanban", "location": {"projectId": 10002, "projectKey": "PROJ2"}},
                    ]
                )
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records([{"id": 3, "name": "Board 3", "type": "scrum", "location": {"projectId": 10003, "projectKey": "PROJ3"}}])
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
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no boards
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraPaginatedResponseBuilder.empty_page("values"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_project_filter(self, http_mocker: HttpMocker):
        """
        Test that connector filters boards based on projects config.

        The boards stream has a record_filter that only includes boards
        whose projectKey is in the config['projects'] list.

        Given: A connector configured with specific projects
        When: Running a full refresh sync
        Then: Only boards matching the project filter should be returned
        """
        config = (
            ConfigBuilder()
            .with_domain(_DOMAIN)
            .with_email(_EMAIL)
            .with_api_token(_API_TOKEN)
            .with_projects(["PROJ1"])  # Only include PROJ1
            .build()
        )

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(
                [
                    {"id": 1, "name": "Board 1", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
                    {"id": 2, "name": "Board 2", "type": "kanban", "location": {"projectId": 10002, "projectKey": "PROJ2"}},
                    {"id": 3, "name": "Board 3", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
                ]
            )
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Only boards with projectKey "PROJ1" should be returned
        assert len(output.records) == 2
        assert all(record.record.data["projectKey"] == "PROJ1" for record in output.records)
