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
_STREAM_NAME = "project_types"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectTypesStream(TestCase):
    """
    Tests for the Jira 'project_types' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/project/type
    Uses selector_base (extracts from root array)
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all project types.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        project_type_records = [
            {
                "key": "software",
                "formattedKey": "Software",
                "descriptionI18nKey": "jira.project.type.software.description",
                "icon": "software-icon",
                "color": "blue",
            },
            {
                "key": "business",
                "formattedKey": "Business",
                "descriptionI18nKey": "jira.project.type.business.description",
                "icon": "business-icon",
                "color": "green",
            },
            {
                "key": "service_desk",
                "formattedKey": "Service Desk",
                "descriptionI18nKey": "jira.project.type.service_desk.description",
                "icon": "service-desk-icon",
                "color": "purple",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.project_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(project_type_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        project_type_keys = [r.record.data["key"] for r in output.records]
        assert "software" in project_type_keys
        assert "business" in project_type_keys
        assert "service_desk" in project_type_keys

    @HttpMocker()
    def test_project_type_properties(self, http_mocker: HttpMocker):
        """
        Test that project type properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        project_type_records = [
            {
                "key": "software",
                "formattedKey": "Software",
                "descriptionI18nKey": "jira.project.type.software.description",
                "icon": "software-icon",
                "color": "blue",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.project_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(project_type_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["key"] == "software"
        assert record["formattedKey"] == "Software"
        assert record["color"] == "blue"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.project_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
