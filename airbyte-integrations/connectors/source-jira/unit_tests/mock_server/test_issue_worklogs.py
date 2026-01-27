# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraJqlResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_worklogs"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueWorklogsStream(TestCase):
    """
    Tests for the Jira 'issue_worklogs' stream.

    This is a semi-incremental (client-side incremental) substream of issues.
    Endpoint: /rest/api/3/issue/{issueIdOrKey}/worklog
    Parent stream: issues (via JQL search)
    Has transformations: AddFields for issueId
    Has incremental_dependency: true
    Extract field: worklogs
    Cursor field: updated (client-side filtering)
    """

    @HttpMocker()
    def test_full_refresh_with_parent_issues(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches worklogs from multiple parent issues.

        Per the playbook: "All substreams should be tested against at least two parent records"
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent issues from JQL search
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

        # Worklogs for issue 10001
        issue1_worklogs = [
            {
                "id": "100001",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100001",
                "author": {
                    "accountId": "user1",
                    "displayName": "User One",
                    "active": True,
                },
                "timeSpent": "2h",
                "timeSpentSeconds": 7200,
                "started": "2024-01-10T09:00:00.000+0000",
                "created": "2024-01-10T10:00:00.000+0000",
                "updated": "2024-01-10T10:00:00.000+0000",
            },
            {
                "id": "100002",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100002",
                "author": {
                    "accountId": "user2",
                    "displayName": "User Two",
                    "active": True,
                },
                "timeSpent": "1h 30m",
                "timeSpentSeconds": 5400,
                "started": "2024-01-12T14:00:00.000+0000",
                "created": "2024-01-12T15:30:00.000+0000",
                "updated": "2024-01-12T15:30:00.000+0000",
            },
        ]

        # Worklogs for issue 10002
        issue2_worklogs = [
            {
                "id": "200001",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10002/worklog/200001",
                "author": {
                    "accountId": "user1",
                    "displayName": "User One",
                    "active": True,
                },
                "timeSpent": "3h",
                "timeSpentSeconds": 10800,
                "started": "2024-01-14T10:00:00.000+0000",
                "created": "2024-01-14T13:00:00.000+0000",
                "updated": "2024-01-14T13:00:00.000+0000",
            },
        ]

        # Mock parent issues endpoint (JQL search)
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=2, is_last=True).build(),
        )

        # Mock worklogs endpoint for issue 10001
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("worklogs")
            .with_records(issue1_worklogs)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock worklogs endpoint for issue 10002
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10002").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("worklogs")
            .with_records(issue2_worklogs)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Should have 3 worklogs total (2 from issue 10001, 1 from issue 10002)
        assert len(output.records) == 3

        # Verify worklog IDs
        worklog_ids = [r.record.data["id"] for r in output.records]
        assert "100001" in worklog_ids
        assert "100002" in worklog_ids
        assert "200001" in worklog_ids

        # Verify issueId transformation is applied
        for record in output.records:
            assert "issueId" in record.record.data

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with prior state.

        The issue_worklogs stream is semi_incremental (client-side filtering).
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # State with cursor for the stream
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": False,
                    "state": {"updated": "2024-01-10T00:00:00.000+0000"},
                    "lookback_window": 0,
                    "states": [{"partition": {"issue_id": "10001"}, "cursor": {"updated": "2024-01-10T00:00:00.000+0000"}}],
                },
            )
            .build()
        )

        # Parent issues from JQL search
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

        # Worklogs (API returns all, client-side filtering applies)
        all_worklogs = [
            {
                "id": "100001",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100001",
                "author": {"accountId": "user1", "displayName": "User One", "active": True},
                "timeSpent": "2h",
                "timeSpentSeconds": 7200,
                "started": "2024-01-08T09:00:00.000+0000",
                "created": "2024-01-08T10:00:00.000+0000",
                "updated": "2024-01-08T10:00:00.000+0000",
            },
            {
                "id": "100002",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100002",
                "author": {"accountId": "user2", "displayName": "User Two", "active": True},
                "timeSpent": "1h",
                "timeSpentSeconds": 3600,
                "started": "2024-01-14T14:00:00.000+0000",
                "created": "2024-01-14T15:00:00.000+0000",
                "updated": "2024-01-14T15:00:00.000+0000",
            },
        ]

        # Mock parent issues endpoint
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        # Mock worklogs endpoint
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("worklogs")
            .with_records(all_worklogs)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        # Client-side filtering should only return worklogs updated after state cursor
        # Worklog 100002 (updated 2024-01-14) should be returned, worklog 100001 (updated 2024-01-08) filtered out
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "100002"

        # Verify state message is emitted
        assert len(output.state_messages) > 0

    @HttpMocker()
    def test_pagination_within_worklogs(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly within the worklogs substream.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent issue
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

        # Worklogs page 1
        page1_worklogs = [
            {
                "id": "100001",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100001",
                "author": {"accountId": "user1", "displayName": "User One", "active": True},
                "timeSpent": "2h",
                "timeSpentSeconds": 7200,
                "started": "2024-01-10T09:00:00.000+0000",
                "created": "2024-01-10T10:00:00.000+0000",
                "updated": "2024-01-10T10:00:00.000+0000",
            },
            {
                "id": "100002",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100002",
                "author": {"accountId": "user1", "displayName": "User One", "active": True},
                "timeSpent": "1h",
                "timeSpentSeconds": 3600,
                "started": "2024-01-11T09:00:00.000+0000",
                "created": "2024-01-11T10:00:00.000+0000",
                "updated": "2024-01-11T10:00:00.000+0000",
            },
        ]

        # Worklogs page 2
        page2_worklogs = [
            {
                "id": "100003",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100003",
                "author": {"accountId": "user2", "displayName": "User Two", "active": True},
                "timeSpent": "3h",
                "timeSpentSeconds": 10800,
                "started": "2024-01-12T09:00:00.000+0000",
                "created": "2024-01-12T12:00:00.000+0000",
                "updated": "2024-01-12T12:00:00.000+0000",
            },
        ]

        # Mock parent issues endpoint
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        # Mock worklogs endpoint with pagination
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10001").with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("worklogs")
                .with_records(page1_worklogs)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("worklogs")
                .with_records(page2_worklogs)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Should have 3 worklogs total
        assert len(output.records) == 3
        worklog_ids = [r.record.data["id"] for r in output.records]
        assert "100001" in worklog_ids
        assert "100002" in worklog_ids
        assert "100003" in worklog_ids

    @HttpMocker()
    def test_empty_parent_issues_no_worklogs(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent issues gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # No parent issues
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
    def test_issue_with_no_worklogs(self, http_mocker: HttpMocker):
        """
        Test that connector handles issues with no worklogs gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent issue
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

        # Mock parent issues endpoint
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        # Mock worklogs endpoint with empty response
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("worklogs")
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
    def test_issueId_transformation_applied(self, http_mocker: HttpMocker):
        """
        Test that the AddFields transformation correctly adds issueId to each record.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent issue
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

        # Worklog without issueId (will be added by transformation)
        worklogs = [
            {
                "id": "100001",
                "self": "https://airbyteio.atlassian.net/rest/api/3/issue/10001/worklog/100001",
                "author": {"accountId": "user1", "displayName": "User One", "active": True},
                "timeSpent": "2h",
                "timeSpentSeconds": 7200,
                "started": "2024-01-10T09:00:00.000+0000",
                "created": "2024-01-10T10:00:00.000+0000",
                "updated": "2024-01-10T10:00:00.000+0000",
            },
        ]

        # Mock parent issues endpoint
        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issue_records).with_pagination(start_at=0, max_results=50, total=1, is_last=True).build(),
        )

        # Mock worklogs endpoint
        http_mocker.get(
            JiraRequestBuilder.issue_worklogs_endpoint(_DOMAIN, "10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("worklogs")
            .with_records(worklogs)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        # Verify issueId transformation is applied with correct value
        assert output.records[0].record.data["issueId"] == "10001"
