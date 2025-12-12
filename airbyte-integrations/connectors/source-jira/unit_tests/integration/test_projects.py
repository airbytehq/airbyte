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
from integration.config import ConfigBuilder
from integration.request_builder import JiraRequestBuilder
from integration.response_builder import JiraErrorResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "projects"
_DOMAIN = "test.atlassian.net"
_EMAIL = "test@example.com"
_API_TOKEN = "test_api_token"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectsStream(TestCase):
    """
    Tests for the Jira 'projects' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Pagination is handled properly (offset-based with startAt/maxResults)
    - Error handling for various HTTP status codes
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of projects.

        Given: A configured Jira connector
        When: Running a full refresh sync for the projects stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(
                [
                    {
                        "id": "10001",
                        "key": "PROJ1",
                        "name": "Project One",
                        "projectTypeKey": "software",
                        "simplified": False,
                        "style": "classic",
                        "isPrivate": False,
                    },
                    {
                        "id": "10002",
                        "key": "PROJ2",
                        "name": "Project Two",
                        "projectTypeKey": "business",
                        "simplified": True,
                        "style": "next-gen",
                        "isPrivate": True,
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
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["key"] == "PROJ1"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[1].record.data["key"] == "PROJ2"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        NOTE: This test validates pagination for the 'projects' stream. Many Jira streams
        use the same DefaultPaginator configuration with startAt/maxResults, so this provides
        pagination coverage for multiple streams.

        Given: An API that returns multiple pages of projects
        When: Running a full refresh sync
        Then: The connector should follow pagination and return all records

        The Jira paginator stop_condition is:
        {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}

        So we need to ensure startAt + maxResults < total for the first page to trigger pagination.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        # Use a list of responses to simulate pagination - responses are returned in order
        # Note: maxResults=2 and total=3 ensures startAt(0) + maxResults(2) < total(3) for first page
        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(
                    [
                        {"id": "10001", "key": "PROJ1", "name": "Project One"},
                        {"id": "10002", "key": "PROJ2", "name": "Project Two"},
                    ]
                )
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records([{"id": "10003", "key": "PROJ3", "name": "Project Three"}])
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
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no projects
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
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
    def test_bad_request_error_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 400 Bad Request errors.

        The Jira manifest configures 400 errors with action: IGNORE, which means the connector
        silently ignores bad request errors and continues the sync.

        Given: An API that returns 400 Bad Request
        When: Running a full refresh sync
        Then: The connector should ignore the error and complete successfully with 0 records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraErrorResponseBuilder.bad_request("Invalid request parameters"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
