# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .analytics_helpers import download_processing_date, read_analytics_stream


_STREAM_NAME = "app_download_historical"


class TestAppDownloadHistoricalStream(TestCase):
    @HttpMocker()
    def test_read_records_and_decode_gzip(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME)
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["Date"] == "2026-01-15"
        assert record["app_id"] == "app-1"
        assert record["processing_date"] == download_processing_date()

    @HttpMocker()
    def test_unavailable_resource_is_ignored(self, http_mocker: HttpMocker) -> None:
        output = read_analytics_stream(http_mocker, _STREAM_NAME, ignored_error=True)
        assert not output.records
