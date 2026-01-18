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
_STREAM_NAME = "issue_properties"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssuePropertiesStream(TestCase):
    """
    Tests for the Jira 'issue_properties' stream.

    This is a 3-level nested substream:
    - Grandparent: issues_stream (provides issue keys)
    - Parent: __issue_property_keys_substream (provides property keys for each issue)
    - Child: issue_properties_stream (gets property values for each key)

    Endpoint: /rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}
    Primary key: key
    Transformations: AddFields (issueId from parent_slice.issue_property_key)
    Uses DpathExtractor with empty field_path (whole response is the record)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_issues_and_properties(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with properties from multiple issues.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock issues endpoint (grandparent stream)
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

        # Mock property keys for issue 1 (parent stream - internal)
        issue1_property_keys = {
            "keys": [
                {"key": "issue.support", "self": "https://example.com/issue/PROJ-1/properties/issue.support"},
            ]
        }

        # Mock property keys for issue 2 (parent stream - internal)
        issue2_property_keys = {
            "keys": [
                {"key": "issue.tracking", "self": "https://example.com/issue/PROJ-2/properties/issue.tracking"},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.issue_properties_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(issue1_property_keys), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_properties_endpoint(_DOMAIN, "PROJ-2").build(),
            HttpResponse(body=json.dumps(issue2_property_keys), status_code=200),
        )

        # Mock individual property values (child stream - the actual exposed stream)
        property1 = {
            "key": "issue.support",
            "value": {"system.conversation.id": "conv-123", "system.support.time": "1m"},
        }
        property2 = {
            "key": "issue.tracking",
            "value": {"tracking.id": "track-456", "tracking.status": "active"},
        }

        http_mocker.get(
            JiraRequestBuilder.issue_property_endpoint(_DOMAIN, "PROJ-1", "issue.support").build(),
            HttpResponse(body=json.dumps(property1), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.issue_property_endpoint(_DOMAIN, "PROJ-2", "issue.tracking").build(),
            HttpResponse(body=json.dumps(property2), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        property_keys = [r.record.data["key"] for r in output.records]
        assert "issue.support" in property_keys
        assert "issue.tracking" in property_keys

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

        # Mock property keys for issue 1
        issue1_property_keys = {
            "keys": [
                {"key": "issue.support", "self": "https://example.com/issue/PROJ-1/properties/issue.support"},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.issue_properties_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(issue1_property_keys), status_code=200),
        )

        # Mock individual property value
        property1 = {
            "key": "issue.support",
            "value": {"system.conversation.id": "conv-123"},
        }

        http_mocker.get(
            JiraRequestBuilder.issue_property_endpoint(_DOMAIN, "PROJ-1", "issue.support").build(),
            HttpResponse(body=json.dumps(property1), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["key"] == "issue.support"
        # The issueId transformation adds the issue key from parent_slice
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
    def test_issue_with_no_property_keys(self, http_mocker: HttpMocker):
        """
        Test that connector handles issues with no property keys gracefully.
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

        # Issue has no property keys
        http_mocker.get(
            JiraRequestBuilder.issue_properties_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps({"keys": []}), status_code=200),
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

        # Mock property keys for issue 1
        issue1_property_keys = {
            "keys": [
                {"key": "issue.support", "self": "https://example.com/issue/PROJ-1/properties/issue.support"},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.issue_properties_endpoint(_DOMAIN, "PROJ-1").build(),
            HttpResponse(body=json.dumps(issue1_property_keys), status_code=200),
        )

        # Property endpoint returns 400 error
        http_mocker.get(
            JiraRequestBuilder.issue_property_endpoint(_DOMAIN, "PROJ-1", "issue.support").build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Bad request"]}), status_code=400),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
