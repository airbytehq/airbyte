# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from integration.config import ConfigBuilder
from integration.request_builder import SentryRequestBuilder
from integration.response_builder import create_response


sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import get_source


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "project_detail"
_ORGANIZATION = "test-org"
_PROJECT = "test-project"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectDetailStream(TestCase):
    """Tests for project_detail stream"""

    def _config(self) -> dict:
        return ConfigBuilder().build()

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test full refresh for project_detail stream"""
        http_mocker.get(
            SentryRequestBuilder.project_detail_endpoint(_ORGANIZATION, _PROJECT, _AUTH_TOKEN).build(),
            create_response("project_detail", has_next=False),
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        assert len(output.records) >= 1, f"Expected project detail record"
        assert output.records[0].record.data["slug"] == "test-project"

    def test_spec_accepts_string_or_array_project(self):
        connector_spec = get_source(config={}).spec(logger=None)

        connection_specification = connector_spec.connectionSpecification
        project_schema = connection_specification["properties"]["project"]

        project_string_schema = project_schema["oneOf"][0]
        project_array_schema = project_schema["oneOf"][1]
        assert project_string_schema["minLength"] == 1
        assert project_string_schema["pattern"] == r"^.*\S.*$"
        assert project_array_schema["minItems"] == 1
        assert project_array_schema["items"]["minLength"] == 1
