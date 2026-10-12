# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .analytics_helpers import analytics_config, expected_record_id, read_analytics_stream


_STREAM_NAME = "analytics_installations_segment_details"


class TestAnalyticsInstallationsSegmentDetailsStream(TestCase):
    @HttpMocker()
    def test_read_records_and_propagate_parent_fields(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME)
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == expected_record_id(_STREAM_NAME)
        assert record["app_id"] == "app-1"

    def test_supports_full_refresh_only(self) -> None:
        config = analytics_config().build()
        stream = next(stream for stream in get_source(config).streams(config=config) if stream.name == _STREAM_NAME)
        assert stream.as_airbyte_stream().supported_sync_modes == [SyncMode.full_refresh]

    @HttpMocker()
    def test_unavailable_resource_is_ignored(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME, ignored_error=True)
        assert not output.records
