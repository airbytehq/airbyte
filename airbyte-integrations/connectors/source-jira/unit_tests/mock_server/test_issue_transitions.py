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
from mock_server.response_builder import JiraJqlResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_transitions"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueTransitionsStream(TestCase):
    """
    Tests for the Jira 'issue_transitions' stream.

    This is a substream that depends on issues as parent.
    Endpoint: /rest/api/3/issue/{issueIdOrKey}/transitions
    Extract field: transitions
    Primary key: [issueId, id]
    Transformations: AddFields (issueId)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_issues(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with transitions from multiple issues.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock issues endpoint (parent stream)
        # Issues must include fields.project for the issues_stream transformations
        issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "updated": "2024-01-15T10:00:00.000+0000",
                    "created": "2024-01-01T10:00:00.000+0000",
                    "project": {"id": "10000", "key": "PROJ"},
                },
            },
            {
                "id": "10002",
                "key": "PROJ-2",
                "fields": {
                    "updated": "2024-01-16T10:00:00.000+0000",
                    "created": "2024-01-02T10:00:00.000+0000",
                    "project": {"id": "10000", "key": "PROJ"},
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issues).with_pagination(start_at=0, max_results=50, total=2).build(),
        )

        # Mock transitions for issue 1
        issue1_transitions = {
            "transitions": [
                {"id": "11", "name": "To Do", "hasScreen": False},
            ]
        }

        # Mock transitions for issue 2
        issue2_transitions = {
            "transitions": [
                {"id": "21", "name": "In Progress", "hasScreen": True},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.issue_transitions_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(issue1_transitions), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_transitions_endpoint(_DOMAIN, "PROJ-2").build(),
            HttpResponse(body=json.dumps(issue2_transitions), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        transition_ids = [r.record.data["id"] for r in output.records]
        assert "11" in transition_ids
        assert "21" in transition_ids

    @HttpMocker()
    def test_issue_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds issueId.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Issues must include fields.project for the issues_stream transformations
        issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "updated": "2024-01-15T10:00:00.000+0000",
                    "created": "2024-01-01T10:00:00.000+0000",
                    "project": {"id": "10000", "key": "PROJ"},
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )

        transitions = {
            "transitions": [
                {"id": "11", "name": "To Do", "hasScreen": False},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.issue_transitions_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(transitions), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "11"
        assert record["issueId"] == "PROJ-1"

    @HttpMocker()
    def test_empty_issues(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty issues gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records([]).with_pagination(start_at=0, max_results=50, total=0).build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_issue_with_no_transitions(self, http_mocker: HttpMocker):
        """
        Test that connector handles issues with no transitions gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Issues must include fields.project for the issues_stream transformations
        issues = [
            {
                "id": "10001",
                "key": "PROJ-1",
                "fields": {
                    "updated": "2024-01-15T10:00:00.000+0000",
                    "created": "2024-01-01T10:00:00.000+0000",
                    "project": {"id": "10000", "key": "PROJ"},
                },
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issues_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraJqlResponseBuilder().with_records(issues).with_pagination(start_at=0, max_results=50, total=1).build(),
        )

        http_mocker.get(
            JiraRequestBuilder.issue_transitions_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps({"transitions": []}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
