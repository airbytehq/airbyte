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
_STREAM_NAME = "time_tracking"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestTimeTrackingStream(TestCase):
    """
    Tests for the Jira 'time_tracking' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/configuration/timetracking/list
    Uses selector_base (extracts from root array)
    Primary key: key
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all time tracking providers.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        time_tracking_records = [
            {
                "key": "JIRA",
                "name": "JIRA provided time tracking",
                "url": f"https://{_DOMAIN}/secure/admin/TimeTrackingAdmin!default.jspa",
            },
            {
                "key": "Tempo",
                "name": "Tempo Timesheets",
                "url": f"https://{_DOMAIN}/plugins/servlet/tempo-get498/",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.time_tracking_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(time_tracking_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        provider_keys = [r.record.data["key"] for r in output.records]
        assert "JIRA" in provider_keys
        assert "Tempo" in provider_keys

    @HttpMocker()
    def test_provider_properties(self, http_mocker: HttpMocker):
        """
        Test that time tracking provider properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        time_tracking_records = [
            {
                "key": "JIRA",
                "name": "JIRA provided time tracking",
                "url": f"https://{_DOMAIN}/secure/admin/TimeTrackingAdmin!default.jspa",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.time_tracking_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(time_tracking_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["key"] == "JIRA"
        assert record["name"] == "JIRA provided time tracking"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.time_tracking_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
