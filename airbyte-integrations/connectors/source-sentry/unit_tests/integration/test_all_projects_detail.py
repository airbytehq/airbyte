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
_STREAM_NAME = "all_projects_detail"
_ORGANIZATION = "test-org"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestAllProjectsDetailStream(TestCase):
    """Tests for all_projects_detail stream (project detail for every org project)"""

    def _config(self) -> dict:
        return ConfigBuilder().build()

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        The stream lists the organization's projects, then fetches project
        detail for each returned project slug via the project-detail endpoint.
        """
        # Parent: org-scoped projects list (returns slug "test-project")
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(),
            create_response("projects", has_next=False),
        )
        # Child: project detail per project slug
        http_mocker.get(
            SentryRequestBuilder.project_detail_endpoint(_ORGANIZATION, "test-project", _AUTH_TOKEN).build(),
            create_response("project_detail", has_next=False),
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        assert len(output.records) >= 1, "Expected all_projects_detail records"
        record = output.records[0].record.data
        assert record["slug"] == "test-project"
        # Fields dropped by the org-scoped list endpoint remain available here.
        assert record["status"] == "active"
