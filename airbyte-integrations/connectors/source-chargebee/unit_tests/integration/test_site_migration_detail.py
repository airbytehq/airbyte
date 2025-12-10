# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import site_migration_detail_response
from .utils import config, read_output


_STREAM_NAME = "site_migration_detail"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestSiteMigrationDetailStream(TestCase):
    """Tests for the site_migration_detail stream (client-side incremental)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for site_migration_detail stream."""
        http_mocker.get(
            RequestBuilder.site_migration_details_endpoint().with_any_query_params().build(),
            site_migration_detail_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["entity_id"] == "smd_001"

    @HttpMocker()
    def test_incremental_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that incremental sync emits state message (client-side incremental with migrated_at cursor)."""
        http_mocker.get(
            RequestBuilder.site_migration_details_endpoint().with_any_query_params().build(),
            site_migration_detail_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1
