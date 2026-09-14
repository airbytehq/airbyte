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
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_custom_field_contexts"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueCustomFieldContextsStream(TestCase):
    """
    Tests for the Jira 'issue_custom_field_contexts' stream.

    This is a substream that depends on custom issue fields as parent.
    Endpoint: /rest/api/3/field/{fieldId}/context
    Extract field: values
    Primary key: id
    Transformations: AddFields (fieldId, fieldType)
    Error handler: 400/403/404 IGNORE
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_fields(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with contexts from multiple custom fields.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock issue fields endpoint (parent stream) - only custom fields are used
        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True, "schema": {"type": "number", "items": None}},
            {"id": "customfield_10002", "name": "Sprint", "custom": True, "schema": {"type": "array", "items": "string"}},
            {"id": "summary", "name": "Summary", "custom": False},  # Non-custom field should be filtered out
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        # Mock contexts for field 1
        field1_contexts = [
            {"id": "10000", "name": "Default Context", "isGlobalContext": True},
        ]

        # Mock contexts for field 2
        field2_contexts = [
            {"id": "10001", "name": "Project Context", "isGlobalContext": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(field1_contexts)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10002").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(field2_contexts)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        context_ids = [r.record.data["id"] for r in output.records]
        assert "10000" in context_ids
        assert "10001" in context_ids

    @HttpMocker()
    def test_field_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds fieldId and fieldType.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True, "schema": {"type": "number", "items": None}},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        contexts = [
            {"id": "10000", "name": "Default Context", "isGlobalContext": True},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(contexts)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["fieldId"] == "customfield_10001"
        assert record["fieldType"] == "number"

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that 400 errors are ignored gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Story Points", "custom": True, "schema": {"type": "number", "items": None}},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10001").with_any_query_params().build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Bad request"]}), status_code=400),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_empty_custom_fields(self, http_mocker: HttpMocker):
        """
        Test that connector handles no custom fields gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Only non-custom fields
        issue_fields = [
            {"id": "summary", "name": "Summary", "custom": False},
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
