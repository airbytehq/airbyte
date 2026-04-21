# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
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
from mock_server.response_builder import JiraAgileResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "board_issues"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestBoardIssuesStream(TestCase):
    """
    Tests for the Jira 'board_issues' stream.

    This is an incremental substream that depends on boards as parent.
    Endpoint: /rest/agile/1.0/board/{boardId}/issue
    Extract field: issues
    Primary key: id
    Cursor field: updated
    Transformations: AddFields (boardId, created, updated)
    Error handler: 500 IGNORE
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
            JiraAgileResponseBuilder("issues").with_records(board1_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )
        http_mocker.get(
            JiraRequestBuilder.board_issues_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraAgileResponseBuilder("issues").with_records(board2_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
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
            JiraAgileResponseBuilder("issues").with_records(board_issues).with_pagination(start_at=0, max_results=50, total=1).build(),
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
        assert not any(log.log.level == "ERROR" for log in output.logs)

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
            JiraAgileResponseBuilder("issues").with_records([]).with_pagination(start_at=0, max_results=50, total=0).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
