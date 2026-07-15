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
_STREAM_NAME = "issue_remote_links"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueRemoteLinksStream(TestCase):
    """
    Tests for the Jira 'issue_remote_links' stream.

    This is a substream that depends on issues as parent.
    Endpoint: /rest/api/3/issue/{issueIdOrKey}/remotelink
    Primary key: id
    Transformations: AddFields (issueId)
    Uses selector_base (root array response)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_issues(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with remote links from multiple issues.
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

        # Mock remote links for issue 1
        issue1_links = [
            {"id": 10100, "globalId": "link1", "self": "https://example.com/link1"},
        ]

        # Mock remote links for issue 2
        issue2_links = [
            {"id": 10101, "globalId": "link2", "self": "https://example.com/link2"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_remote_links_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(issue1_links), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_remote_links_endpoint(_DOMAIN, "PROJ-2").build(),
            HttpResponse(body=json.dumps(issue2_links), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        link_ids = [r.record.data["id"] for r in output.records]
        assert 10100 in link_ids
        assert 10101 in link_ids

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

        remote_links = [
            {"id": 10100, "globalId": "link1", "self": "https://example.com/link1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_remote_links_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(remote_links), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 10100
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
    def test_issue_with_no_remote_links(self, http_mocker: HttpMocker):
        """
        Test that connector handles issues with no remote links gracefully.
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
            JiraRequestBuilder.issue_remote_links_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that 400 errors are ignored gracefully.

        Per manifest.yaml, the default error_handler has:
        http_codes: [400] -> action: IGNORE
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

        # Remote links endpoint returns 400 error
        http_mocker.get(
            JiraRequestBuilder.issue_remote_links_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Bad request"]}), status_code=400),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
