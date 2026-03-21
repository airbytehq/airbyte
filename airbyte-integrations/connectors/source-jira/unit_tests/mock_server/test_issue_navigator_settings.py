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
_STREAM_NAME = "issue_navigator_settings"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueNavigatorSettingsStream(TestCase):
    """
    Tests for the Jira 'issue_navigator_settings' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/settings/columns
    Uses selector_base (extracts from root array)
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all navigator settings.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        settings_records = [
            {"label": "Key", "value": "issuekey"},
            {"label": "Summary", "value": "summary"},
            {"label": "Status", "value": "status"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_navigator_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(settings_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        labels = [r.record.data["label"] for r in output.records]
        assert "Key" in labels
        assert "Summary" in labels
        assert "Status" in labels

    @HttpMocker()
    def test_setting_properties(self, http_mocker: HttpMocker):
        """
        Test that setting properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        settings_records = [
            {"label": "Priority", "value": "priority"},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_navigator_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(settings_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["label"] == "Priority"
        assert record["value"] == "priority"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_navigator_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
