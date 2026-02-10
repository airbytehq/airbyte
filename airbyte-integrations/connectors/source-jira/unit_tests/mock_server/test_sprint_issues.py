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
from mock_server.response_builder import JiraAgileResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "sprint_issues"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestSprintIssuesStream(TestCase):
    """
    Tests for the Jira 'sprint_issues' stream.

    This is an incremental substream that depends on sprints as parent.
    Uses SprintIssuesSubstreamPartitionRouter custom component.
    Endpoint: /rest/agile/1.0/sprint/{sprintId}/issue
    Extract field: issues
    Primary key: id (composite: sprintId-issueId)
    Cursor field: updated
    Transformations: AddFields (issueId, id, sprintId, created, updated)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_sprints(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with issues from multiple sprints.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock boards endpoint (parent of sprints)
        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock sprints endpoint (parent stream)
        sprints = [
            {"id": 1, "name": "Sprint 1", "state": "closed", "boardId": 1},
            {"id": 2, "name": "Sprint 2", "state": "active", "boardId": 1},
        ]

        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(sprints)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock issue fields endpoint (for story points field)
        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        # Mock sprint issues for sprint 1
        sprint1_issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "created": "2024-01-01T10:00:00.000+0000",
                    "updated": "2024-01-15T10:00:00.000+0000",
                },
            },
        ]

        # Mock sprint issues for sprint 2
        sprint2_issues = [
            {
                "id": "10002",
                "key": "PROJ-2",
                "fields": {
                    "created": "2024-01-02T10:00:00.000+0000",
                    "updated": "2024-01-16T10:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.sprint_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraAgileResponseBuilder("issues").with_records(sprint1_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )
        http_mocker.get(
            JiraRequestBuilder.sprint_issues_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraAgileResponseBuilder("issues").with_records(sprint2_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        issue_ids = [r.record.data["issueId"] for r in output.records]
        assert "10001" in issue_ids
        assert "10002" in issue_ids

    @HttpMocker()
    def test_sprint_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds sprintId, issueId, created, updated.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        sprints = [
            {"id": 1, "name": "Sprint 1", "state": "active", "boardId": 1},
        ]

        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(sprints)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        sprint_issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "created": "2024-01-01T10:00:00.000+0000",
                    "updated": "2024-01-15T10:00:00.000+0000",
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.sprint_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraAgileResponseBuilder("issues").with_records(sprint_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["sprintId"] == 1
        assert record["issueId"] == "10001"
        assert record["id"] == "1-10001"
        assert record["created"] == "2024-01-01T10:00:00.000+0000"
        assert record["updated"] == "2024-01-15T10:00:00.000+0000"

    @HttpMocker()
    def test_empty_sprints(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty sprints gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([])
            .with_pagination(start_at=0, max_results=50, total=0, is_last=True)
            .build(),
        )

        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_sprint_with_no_issues(self, http_mocker: HttpMocker):
        """
        Test that connector handles sprints with no issues gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        sprints = [
            {"id": 1, "name": "Sprint 1", "state": "active", "boardId": 1},
        ]

        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(sprints)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        http_mocker.get(
            JiraRequestBuilder.sprint_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraAgileResponseBuilder("issues").with_records([]).with_pagination(start_at=0, max_results=50, total=0).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
