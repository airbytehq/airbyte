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
_STREAM_NAME = "issue_custom_field_options"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueCustomFieldOptionsStream(TestCase):
    """
    Tests for the Jira 'issue_custom_field_options' stream.

    This is a nested substream that depends on issue_custom_field_contexts.
    Endpoint: /rest/api/3/field/{fieldId}/context/{contextId}/option
    Extract field: values
    Primary key: id
    Transformations: AddFields (fieldId, contextId)
    Error handler: 400/403/404 IGNORE
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_contexts(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with options from multiple contexts.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock issue fields endpoint (grandparent stream) - only custom fields with option type
        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        # Mock contexts for field (parent stream)
        contexts = [
            {"id": "10000", "name": "Default Context", "isGlobalContext": True},
            {"id": "10001", "name": "Project Context", "isGlobalContext": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(contexts)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock options for context 1
        context1_options = [
            {"id": "10100", "value": "High", "disabled": False},
        ]

        # Mock options for context 2
        context2_options = [
            {"id": "10101", "value": "Low", "disabled": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10000").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(context1_options)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10001").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(context2_options)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        option_ids = [r.record.data["id"] for r in output.records]
        assert "10100" in option_ids
        assert "10101" in option_ids

    @HttpMocker()
    def test_context_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds fieldId and contextId.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
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

        options = [
            {"id": "10100", "value": "High", "disabled": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10000").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(options)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["fieldId"] == "customfield_10001"
        assert record["contextId"] == "10000"

    @HttpMocker()
    def test_error_404_ignored(self, http_mocker: HttpMocker):
        """
        Test that 404 errors are ignored gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
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

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10000").with_any_query_params().build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Not found"]}), status_code=404),
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

        Per manifest.yaml, the error_handler for this stream has:
        http_codes: [400, 403, 404] -> action: IGNORE
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
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

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10000").with_any_query_params().build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Bad request"]}), status_code=400),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_error_403_ignored(self, http_mocker: HttpMocker):
        """
        Test that 403 errors are ignored gracefully.

        Per manifest.yaml, the error_handler for this stream has:
        http_codes: [400, 403, 404] -> action: IGNORE
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
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

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_options_endpoint(_DOMAIN, "customfield_10001", "10000").with_any_query_params().build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Forbidden"]}), status_code=403),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_empty_contexts(self, http_mocker: HttpMocker):
        """
        Test that connector handles no contexts gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issue_fields = [
            {"id": "customfield_10001", "name": "Priority", "custom": True, "schema": {"type": "option", "items": None}},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_fields_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(issue_fields), status_code=200),
        )

        http_mocker.get(
            JiraRequestBuilder.issue_custom_field_contexts_endpoint(_DOMAIN, "customfield_10001").with_any_query_params().build(),
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
