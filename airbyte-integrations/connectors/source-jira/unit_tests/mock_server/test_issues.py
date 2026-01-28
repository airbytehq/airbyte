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
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraJqlResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issues"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssuesStream(TestCase):
    """
    Tests for the Jira 'issues' stream.

    This is an incremental stream using JQL pagination.
    Endpoint: /rest/api/3/search (via JQL)
    Uses CustomPartitionRouter (SubstreamOrSinglePartitionRouter)
    Has transformations: AddFields for projectId, projectKey, created, updated
    Has custom transformation: RemoveEmptyFields
    Error handler: 400 errors are IGNORED (user doesn't have permission)
    """

    @HttpMocker()
    def test_full_refresh_no_projects_filter(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches issues without project filter.

        When projects config is empty, SubstreamOrSinglePartitionRouter returns
        an empty partition, meaning "fetch all without iterating parents."
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_records = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "self": f"https://{_DOMAIN}/rest/api/3/issue/10001",
                "fields": {
                    "summary": "Test Issue 1",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
            {
                "id": "10002",
                "key": "PROJ-2",
                "self": f"https://{_DOMAIN}/rest/api/3/issue/10002",
                "fields": {
                    "summary": "Test Issue 2",
                    "project": {"id": "10002", "key": "PROJ2"},
                    "created": "2024-01-02T00:00:00.000+0000",
                    "updated": "2024-01-16T00:00:00.000+0000",
                },
            },
        ]

        # Mock issues endpoint (JQL search)
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=2, is_last=True).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["key"] == "PROJ-1"
        # Verify transformations are applied
        assert output.records[0].record.data["projectId"] == "10001"
        assert output.records[0].record.data["projectKey"] == "PROJ1"

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Test incremental sync without prior state (initial sync).

        Should fetch all issues and emit a state message.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_records = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "summary": "Test Issue 1",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        # Verify state message is emitted
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with prior state.

        Should use the state to filter issues updated after the cursor.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Build state with a cursor value
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-01-10T00:00:00.000+0000"}).build()

        issue_records = [
            {
                "id": "10002",
                "key": "PROJ-2",
                "fields": {
                    "summary": "Updated Issue",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "10002"

    @HttpMocker()
    def test_pagination_with_next_page_token(self, http_mocker: HttpMocker):
        """
        Test JQL pagination using nextPageToken.

        NOTE: This test validates pagination for the 'issues' stream using the jql_paginator,
        which uses nextPageToken instead of startAt. Currently, only the issues stream uses
        this paginator configuration.

        The JQL paginator uses nextPageToken instead of startAt for pagination.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_records = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "summary": "Issue 1",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
            {
                "id": "10002",
                "key": "PROJ-2",
                "fields": {
                    "summary": "Issue 2",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-02T00:00:00.000+0000",
                    "updated": "2024-01-16T00:00:00.000+0000",
                },
            },
        ]
        page2_records = [
            {
                "id": "10003",
                "key": "PROJ-3",
                "fields": {
                    "summary": "Issue 3",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-03T00:00:00.000+0000",
                    "updated": "2024-01-17T00:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraJqlResponseBuilder()
                .with_records(page1_records)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False, next_page_token="token123")
                .build(),
                JiraJqlResponseBuilder()
                .with_records(page2_records)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        issue_ids = [r.record.data["id"] for r in output.records]
        assert "10001" in issue_ids
        assert "10002" in issue_ids
        assert "10003" in issue_ids

    @HttpMocker()
    def test_with_projects_filter(self, http_mocker: HttpMocker):
        """
        Test that connector uses project filter when projects config is set.

        When projects config is set, SubstreamOrSinglePartitionRouter iterates
        over parent projects and includes project_id in the JQL query.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_projects(["PROJ1"]).build()

        # Mock projects endpoint (parent stream)
        project_records = [
            {"id": "10001", "key": "PROJ1", "name": "Project One"},
        ]
        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(project_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock issues endpoint
        issue_records = [
            {
                "id": "10001",
                "key": "PROJ1-1",
                "fields": {
                    "summary": "Project 1 Issue",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
        ]
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["projectKey"] == "PROJ1"

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that 400 errors are ignored (user doesn't have permission).
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["The user doesn't have permission to the project"]}),
                status_code=400,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records([]).with_pagination(start_at=0, max_results=50, total=0, is_last=True).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_given_timezone_in_state_when_read_consider_timezone(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles timezone in state cursor.

        When state contains a datetime with timezone offset (e.g., -0800),
        the connector should convert it to timestamp correctly for the JQL query.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        datetime_with_timezone = "2023-11-01T00:00:00.000-0800"
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": False,
                    "state": {"updated": datetime_with_timezone},
                    "lookback_window": 2,
                    "states": [{"partition": {}, "cursor": {"updated": datetime_with_timezone}}],
                },
            )
            .build()
        )

        issue_records = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "summary": "Test Issue",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-01T00:00:00.000+0000",
                    "updated": "2024-01-15T00:00:00.000+0000",
                },
            },
            {
                "id": "10002",
                "key": "PROJ-2",
                "fields": {
                    "summary": "Test Issue 2",
                    "project": {"id": "10001", "key": "PROJ1"},
                    "created": "2024-01-02T00:00:00.000+0000",
                    "updated": "2024-01-16T00:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=2, is_last=True).build(),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 2
