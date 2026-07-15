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


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_types"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueTypesStream(TestCase):
    """
    Tests for the Jira 'issue_types' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/issuetype
    Uses selector_base (extracts from root array)
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all issue types.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_type_records = [
            {
                "id": "10000",
                "name": "Bug",
                "description": "A problem which impairs or prevents the functions of the product.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/issuetypes/bug.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/issuetype/10000",
                "subtask": False,
                "hierarchyLevel": 0,
            },
            {
                "id": "10001",
                "name": "Story",
                "description": "A user story.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/issuetypes/story.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/issuetype/10001",
                "subtask": False,
                "hierarchyLevel": 0,
            },
            {
                "id": "10002",
                "name": "Sub-task",
                "description": "A sub-task of an issue.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/issuetypes/subtask.svg",
                "self": f"https://{_DOMAIN}/rest/api/3/issuetype/10002",
                "subtask": True,
                "hierarchyLevel": -1,
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_type_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        issue_type_ids = [r.record.data["id"] for r in output.records]
        assert "10000" in issue_type_ids
        assert "10001" in issue_type_ids
        assert "10002" in issue_type_ids

    @HttpMocker()
    def test_subtask_property(self, http_mocker: HttpMocker):
        """
        Test that subtask property is correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_type_records = [
            {
                "id": "10002",
                "name": "Sub-task",
                "description": "A sub-task of an issue.",
                "subtask": True,
                "hierarchyLevel": -1,
                "self": f"https://{_DOMAIN}/rest/api/3/issuetype/10002",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_type_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["subtask"] is True
        assert record["hierarchyLevel"] == -1

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
