# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "issue_field_configurations"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueFieldConfigurationsStream(TestCase):
    """
    Tests for the Jira 'issue_field_configurations' stream.

    Endpoint: /rest/api/3/fieldconfiguration
    Extract field: values
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all field configurations.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        field_configs = [
            {"id": 10000, "name": "Default Field Configuration", "description": "Default", "isDefault": True},
            {"id": 10001, "name": "Custom Field Configuration", "description": "Custom", "isDefault": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_field_configurations_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(field_configs)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        config_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in config_ids
        assert 10001 in config_ids

    @HttpMocker()
    def test_pagination(self, http_mocker: HttpMocker):
        """
        Test pagination with 2 pages of field configurations.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_configs = [
            {"id": 10000, "name": "Config 1", "isDefault": True},
            {"id": 10001, "name": "Config 2", "isDefault": False},
        ]

        page2_configs = [
            {"id": 10002, "name": "Config 3", "isDefault": False},
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_field_configurations_endpoint(_DOMAIN).with_query_param("maxResults", "50").build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(page1_configs)
            .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
            .build(),
        )

        http_mocker.get(
            JiraRequestBuilder.issue_field_configurations_endpoint(_DOMAIN)
            .with_query_param("maxResults", "50")
            .with_query_param("startAt", "2")
            .build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(page2_configs)
            .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        config_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in config_ids
        assert 10001 in config_ids
        assert 10002 in config_ids

    @HttpMocker()
    def test_empty_response(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty response gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_field_configurations_endpoint(_DOMAIN).with_any_query_params().build(),
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
