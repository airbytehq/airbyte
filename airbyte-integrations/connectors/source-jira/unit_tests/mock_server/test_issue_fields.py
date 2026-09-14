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
_STREAM_NAME = "issue_fields"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueFieldsStream(TestCase):
    """
    Tests for the Jira 'issue_fields' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/field
    Primary key: id
    Uses retriever_no_pagination_use_cache
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all issue fields.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        field_records = [
            {
                "id": "summary",
                "key": "summary",
                "name": "Summary",
                "custom": False,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["summary"],
            },
            {
                "id": "description",
                "key": "description",
                "name": "Description",
                "custom": False,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["description"],
            },
            {
                "id": "customfield_10001",
                "key": "customfield_10001",
                "name": "Story Points",
                "custom": True,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["cf[10001]", "Story Points"],
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(field_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        field_ids = [r.record.data["id"] for r in output.records]
        assert "summary" in field_ids
        assert "description" in field_ids
        assert "customfield_10001" in field_ids

    @HttpMocker()
    def test_custom_field_properties(self, http_mocker: HttpMocker):
        """
        Test that custom field properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        field_records = [
            {
                "id": "customfield_10001",
                "key": "customfield_10001",
                "name": "Story Points",
                "custom": True,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["cf[10001]", "Story Points"],
                "scope": {"type": "PROJECT", "project": {"id": "10000"}},
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(field_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["custom"] is True
        assert record["name"] == "Story Points"
        assert "scope" in record

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
