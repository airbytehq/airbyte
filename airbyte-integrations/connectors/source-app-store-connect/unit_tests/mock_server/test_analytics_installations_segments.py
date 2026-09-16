# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .analytics_helpers import expected_record_id, processing_date, read_analytics_stream
from .utils import latest_stream_state


_STREAM_NAME = "analytics_installations_segments"


class TestAnalyticsInstallationsSegmentsStream(TestCase):
    @HttpMocker()
    def test_read_records_and_propagate_parent_fields(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME)
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == expected_record_id(_STREAM_NAME)
        assert record["app_id"] == "app-1"

    @HttpMocker()
    def test_pagination_follows_next_link(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME, paginate=True)
        expected_id = expected_record_id(_STREAM_NAME)
        assert {record.record.data["id"] for record in output.records} == {
            expected_id,
            f"{expected_id}-page-2",
        }

    @HttpMocker()
    def test_incremental_sync_uses_state(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME, incremental=True)
        assert len(output.records) == 1
        assert latest_stream_state(output, "processing_date") == processing_date()

    @HttpMocker()
    def test_unavailable_resource_is_ignored(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME, ignored_error=True)
        assert not output.records
