# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase
import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker

from integration.config import ConfigBuilder
from integration.request_builder import SentryRequestBuilder
from integration.response_builder import create_response

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import get_source

_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "projects"
_ORGANIZATION = "test-org"
_AUTH_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectsStream(TestCase):
    """Tests for projects stream"""

    def _config(self) -> dict:
        return ConfigBuilder().build()

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test full refresh for projects stream"""
        http_mocker.get(
            SentryRequestBuilder.projects_endpoint(_ORGANIZATION, _AUTH_TOKEN).build(),
            create_response("projects", has_next=False)
        )

        source = get_source(config=self._config())
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=self._config(), catalog=catalog)

        assert len(output.records) >= 1, f"Expected project records"
        assert output.records[0].record.data["slug"] == "test-project"
