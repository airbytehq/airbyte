# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import ExpectedOutcome, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraPaginatedResponseBuilder, JiraSoftwareIssuesResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "board_issues"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestBoardIssuesStream(TestCase):
    """
    Tests for the Jira 'board_issues' stream.

    This is an incremental substream that depends on boards as parent.
    Endpoint: /rest/software/1.0/board/{boardId}/issue
    Extract field: issues
    Primary key: id
    Cursor field: updated
    Transformations: AddFields (boardId, created, updated)
    Error handler: IGNORE any status whose errorMessages mention "no columns with a mapped status"; other 5xx are retried
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_boards(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with issues from multiple boards.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock boards endpoint (parent stream)
        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
            {"id": 2, "name": "Board 2", "type": "kanban"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock board issues for board 1
        board1_issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "created": "2024-01-01T10:00:00.000+0000",
                    "updated": "2024-01-15T10:00:00.000+0000",
                },
            },
        ]

        # Mock board issues for board 2
        board2_issues = [
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
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records(board1_issues).build(),
        )
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records(board2_issues).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        issue_ids = [r.record.data["id"] for r in output.records]
        assert "10001" in issue_ids
        assert "10002" in issue_ids

    @HttpMocker()
    def test_board_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds boardId, created, updated.
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

        board_issues = [
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
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records(board_issues).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["boardId"] == 1
        assert record["created"] == "2024-01-01T10:00:00.000+0000"
        assert record["updated"] == "2024-01-15T10:00:00.000+0000"

    @HttpMocker()
    def test_empty_boards(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty boards gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([])
            .with_pagination(start_at=0, max_results=50, total=0, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert output.errors == []

    @HttpMocker()
    def test_board_with_no_issues(self, http_mocker: HttpMocker):
        """
        Test that connector handles boards with no issues gracefully.
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
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records([]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert output.errors == []

    @HttpMocker()
    def test_ignores_board_without_mapped_status_columns(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_domain(_DOMAIN).build()
        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
            {"id": 2, "name": "Board 2", "type": "kanban"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "errorMessages": ["This board has no columns with a mapped status."],
                        "errors": {},
                    }
                ),
                status_code=400,
            ),
        )
        board_2_issue = {
            "id": "10002",
            "key": "PROJ-2",
            "fields": {
                "created": "2024-01-02T10:00:00.000+0000",
                "updated": "2024-01-16T10:00:00.000+0000",
            },
        }
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records([board_2_issue]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert [record.record.data["id"] for record in output.records] == ["10002"]
        assert output.errors == []

    @HttpMocker()
    def test_does_not_ignore_other_board_400_errors(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_domain(_DOMAIN).build()
        boards = [
            {"id": 1, "name": "Board 1", "type": "scrum"},
            {"id": 2, "name": "Board 2", "type": "kanban"},
        ]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(boards)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "errorMessages": ["The value 'x' does not exist for the field 'project'."],
                        "errors": {},
                    }
                ),
                status_code=400,
            ),
        )
        board_2_issue = {
            "id": "10002",
            "key": "PROJ-2",
            "fields": {
                "created": "2024-01-02T10:00:00.000+0000",
                "updated": "2024-01-16T10:00:00.000+0000",
            },
        }
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraSoftwareIssuesResponseBuilder().with_records([board_2_issue]).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        with self.assertLogs(level="ERROR") as error_logs:
            output = read(source, config=config, catalog=catalog, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        assert [record.record.data["id"] for record in output.records] == ["10002"]
        assert any("The value 'x' does not exist for the field 'project'." in message for message in error_logs.output)

    @HttpMocker()
    def test_retries_other_board_500_errors(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_domain(_DOMAIN).build()
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([{"id": 1, "name": "Board 1", "type": "scrum"}])
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )
        board_issues_request = JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1").with_any_query_params().build()
        board_issue = {
            "id": "10001",
            "key": "PROJ-1",
            "fields": {
                "created": "2024-01-01T10:00:00.000+0000",
                "updated": "2024-01-15T10:00:00.000+0000",
            },
        }
        http_mocker.get(
            board_issues_request,
            [
                HttpResponse(body=json.dumps({"errorMessages": ["Internal server error"], "errors": {}}), status_code=500),
                JiraSoftwareIssuesResponseBuilder().with_records([board_issue]).build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        with patch("time.sleep"):
            output = read(source, config=config, catalog=catalog)

        assert [record.record.data["id"] for record in output.records] == ["10001"]
        http_mocker.assert_number_of_calls(board_issues_request, 2)

    @HttpMocker()
    def test_cursor_pagination(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_domain(_DOMAIN).build()
        board = [{"id": 1, "name": "Board 1", "type": "scrum"}]

        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(board)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        page_1_request = (
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1")
            .with_fields(["key", "created", "updated"])
            .with_jql("updated >= 1609459200000 ORDER BY updated asc")
            .with_max_results(50)
            .build()
        )
        page_2_request = (
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "1")
            .with_fields(["key", "created", "updated"])
            .with_jql("updated >= 1609459200000 ORDER BY updated asc")
            .with_max_results(50)
            .with_next_page_token("page-2-token")
            .build()
        )
        page_1_issue = {
            "id": "10001",
            "key": "PROJ-1",
            "fields": {
                "created": "2024-01-01T10:00:00.000+0000",
                "updated": "2024-01-15T10:00:00.000+0000",
            },
        }
        page_2_issue = {
            "id": "10002",
            "key": "PROJ-2",
            "fields": {
                "created": "2024-01-02T10:00:00.000+0000",
                "updated": "2024-01-16T10:00:00.000+0000",
            },
        }
        http_mocker.get(
            page_1_request,
            JiraSoftwareIssuesResponseBuilder().with_records([page_1_issue]).with_next_page_token("page-2-token").build(),
        )
        http_mocker.get(page_2_request, JiraSoftwareIssuesResponseBuilder().with_records([page_2_issue]).build())

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert [record.record.data["id"] for record in output.records] == ["10001", "10002"]
        http_mocker.assert_number_of_calls(page_1_request, 1)
        http_mocker.assert_number_of_calls(page_2_request, 1)
