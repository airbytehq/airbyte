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
_STREAM_NAME = "sprints"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestSprintsStream(TestCase):
    """
    Tests for the Jira 'sprints' stream.

    This is a substream of boards using SubstreamPartitionRouter.
    Endpoint: /rest/agile/1.0/board/{boardId}/sprint
    Parent stream: boards (filtered to scrum/simple types only)
    Has transformations: AddFields for boardId
    Error handler: 400 errors are IGNORED (board doesn't support sprints)
    """

    @HttpMocker()
    def test_full_refresh_with_parent_boards(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches sprints from multiple parent boards.

        Per the playbook: "All substreams should be tested against at least two parent records"
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent boards (only scrum/simple types are used for sprints)
        board_records = [
            {"id": 1, "name": "Scrum Board 1", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
            {"id": 2, "name": "Scrum Board 2", "type": "scrum", "location": {"projectId": 10002, "projectKey": "PROJ2"}},
        ]

        # Sprints for board 1
        board1_sprints = [
            {
                "id": 101,
                "name": "Sprint 1",
                "state": "active",
                "startDate": "2024-01-01T00:00:00.000Z",
                "endDate": "2024-01-14T00:00:00.000Z",
                "originBoardId": 1,
            },
            {
                "id": 102,
                "name": "Sprint 2",
                "state": "future",
                "originBoardId": 1,
            },
        ]

        # Sprints for board 2
        board2_sprints = [
            {
                "id": 201,
                "name": "Sprint A",
                "state": "closed",
                "startDate": "2024-01-01T00:00:00.000Z",
                "endDate": "2024-01-14T00:00:00.000Z",
                "completeDate": "2024-01-14T00:00:00.000Z",
                "originBoardId": 2,
            },
        ]

        # Mock parent boards endpoint
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock sprints endpoint for board 1
        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board1_sprints)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock sprints endpoint for board 2
        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "2").with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board2_sprints)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Should have 3 sprints total (2 from board 1, 1 from board 2)
        assert len(output.records) == 3

        # Verify sprints from board 1
        sprint_ids = [r.record.data["id"] for r in output.records]
        assert 101 in sprint_ids
        assert 102 in sprint_ids
        assert 201 in sprint_ids

        # Verify boardId transformation is applied
        for record in output.records:
            assert "boardId" in record.record.data

    @HttpMocker()
    def test_board_without_sprints_error_ignored(self, http_mocker: HttpMocker):
        """
        Test that 400 errors are ignored when a board doesn't support sprints.

        The error handler in manifest:
        - http_codes: [400]
        - action: IGNORE
        - error_message: "The board does not support sprints..."
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent boards - one scrum board
        board_records = [
            {"id": 1, "name": "Scrum Board", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
        ]

        # Mock parent boards endpoint
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock sprints endpoint returning 400 error (board doesn't support sprints)
        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["The board does not support sprints"]}),
                status_code=400,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        # Should have 0 sprints since the board doesn't support them
        assert len(output.records) == 0

    @HttpMocker()
    def test_pagination_within_sprints(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly within the sprints substream.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Parent board
        board_records = [
            {"id": 1, "name": "Scrum Board", "type": "scrum", "location": {"projectId": 10001, "projectKey": "PROJ1"}},
        ]

        # Sprints page 1
        page1_sprints = [
            {"id": 101, "name": "Sprint 1", "state": "closed", "originBoardId": 1},
            {"id": 102, "name": "Sprint 2", "state": "closed", "originBoardId": 1},
        ]

        # Sprints page 2
        page2_sprints = [
            {"id": 103, "name": "Sprint 3", "state": "active", "originBoardId": 1},
        ]

        # Mock parent boards endpoint
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values")
            .with_records(board_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock sprints endpoint with pagination
        http_mocker.get(
            JiraRequestBuilder.sprints_endpoint(_DOMAIN, "1").with_any_query_params().build(),
            [
                JiraAgileResponseBuilder("values")
                .with_records(page1_sprints)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraAgileResponseBuilder("values")
                .with_records(page2_sprints)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Should have 3 sprints total
        assert len(output.records) == 3
        sprint_ids = [r.record.data["id"] for r in output.records]
        assert 101 in sprint_ids
        assert 102 in sprint_ids
        assert 103 in sprint_ids

    @HttpMocker()
    def test_empty_boards_no_sprints(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent boards gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # No parent boards
        http_mocker.get(
            JiraRequestBuilder.boards_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraAgileResponseBuilder("values").with_records([]).with_pagination(start_at=0, max_results=50, total=0, is_last=True).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
