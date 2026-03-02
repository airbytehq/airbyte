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
_STREAM_NAME = "workflow_statuses"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestWorkflowStatusesStream(TestCase):
    """
    Tests for the Jira 'workflow_statuses' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/status
    Uses selector_base (extracts from root array)
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all workflow statuses.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        status_records = [
            {
                "id": "1",
                "name": "Open",
                "description": "The issue is open and ready for the assignee to start work on it.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/statuses/open.png",
                "statusCategory": {"id": 2, "key": "new", "name": "To Do"},
            },
            {
                "id": "3",
                "name": "In Progress",
                "description": "This issue is being actively worked on at the moment by the assignee.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/statuses/inprogress.png",
                "statusCategory": {"id": 4, "key": "indeterminate", "name": "In Progress"},
            },
            {
                "id": "6",
                "name": "Closed",
                "description": "The issue is considered finished.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/statuses/closed.png",
                "statusCategory": {"id": 3, "key": "done", "name": "Done"},
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflow_statuses_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(status_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        status_ids = [r.record.data["id"] for r in output.records]
        assert "1" in status_ids
        assert "3" in status_ids
        assert "6" in status_ids

    @HttpMocker()
    def test_status_properties(self, http_mocker: HttpMocker):
        """
        Test that workflow status properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        status_records = [
            {
                "id": "1",
                "name": "Open",
                "description": "The issue is open.",
                "iconUrl": f"https://{_DOMAIN}/images/icons/statuses/open.png",
                "statusCategory": {"id": 2, "key": "new", "name": "To Do"},
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflow_statuses_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(status_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "1"
        assert record["name"] == "Open"
        assert "statusCategory" in record

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.workflow_statuses_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
