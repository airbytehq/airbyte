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
_STREAM_NAME = "jira_settings"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestJiraSettingsStream(TestCase):
    """
    Tests for the Jira 'jira_settings' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/application-properties
    Uses selector_base (extracts from root array)
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all jira settings.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        settings_records = [
            {
                "id": "jira.home",
                "key": "jira.home",
                "value": "/var/atlassian/application-data/jira",
                "name": "jira.home",
                "desc": "Jira home directory",
                "type": "string",
            },
            {
                "id": "jira.title",
                "key": "jira.title",
                "value": "Airbyte Jira",
                "name": "jira.title",
                "desc": "The name of this JIRA installation.",
                "type": "string",
            },
            {
                "id": "jira.baseurl",
                "key": "jira.baseurl",
                "value": f"https://{_DOMAIN}",
                "name": "jira.baseurl",
                "desc": "The base URL of this JIRA installation.",
                "type": "string",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.jira_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(settings_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        setting_ids = [r.record.data["id"] for r in output.records]
        assert "jira.home" in setting_ids
        assert "jira.title" in setting_ids
        assert "jira.baseurl" in setting_ids

    @HttpMocker()
    def test_setting_properties(self, http_mocker: HttpMocker):
        """
        Test that setting properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        settings_records = [
            {
                "id": "jira.option.allowunassignedissues",
                "key": "jira.option.allowunassignedissues",
                "value": "true",
                "name": "Allow unassigned issues",
                "desc": "Allow issues to be unassigned.",
                "type": "boolean",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.jira_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(settings_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "jira.option.allowunassignedissues"
        assert record["value"] == "true"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.jira_settings_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
