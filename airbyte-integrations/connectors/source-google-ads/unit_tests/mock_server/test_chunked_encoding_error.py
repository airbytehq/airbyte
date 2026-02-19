# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

from requests.exceptions import ChunkedEncodingError

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    build_stream_response,
    mock_incremental_stream,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"
_STREAM_NAME = "ad_group"

_RECORD_FIRST_HALF = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400001",
        "name": "Ad Group First Half",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-03"},
    "metrics": {"costMicros": "1000000"},
}

_RECORD_SECOND_HALF = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400002",
        "name": "Ad Group Second Half",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-10"},
    "metrics": {"costMicros": "2000000"},
}

_RECORD_SINGLE_DAY = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400003",
        "name": "Ad Group Single Day",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-01"},
    "metrics": {"costMicros": "500000"},
}


def test_chunked_encoding_error_triggers_slice_split():
    """
    When ChunkedEncodingError occurs on the first read, GoogleAdsRetriever
    splits the 14-day date range into two 7-day sub-slices and retries each.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-07",
            response=build_stream_response([_RECORD_FIRST_HALF]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-08",
            end_date="2024-01-14",
            response=build_stream_response([_RECORD_SECOND_HALF]),
        )

        original_read_pages = SimpleRetriever._read_pages
        call_count = 0

        def read_pages_raising_first_call(self, records_generator_fn, stream_slice):
            nonlocal call_count
            cursor = getattr(stream_slice, "cursor_slice", {})
            is_target = cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-14"
            if is_target:
                call_count += 1
                if call_count == 1:
                    raise ChunkedEncodingError("simulated midstream break")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_raising_first_call):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 2
    ad_group_ids = sorted(r.record.data["ad_group.id"] for r in output.records)
    assert ad_group_ids == [400001, 400002]


def test_chunked_encoding_error_retries_on_minimum_slice():
    """
    When ChunkedEncodingError occurs on a 1-day (minimum) slice that cannot
    be split further, GoogleAdsRetriever retries the same slice and succeeds.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-01").build()

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-01",
            response=build_stream_response([_RECORD_SINGLE_DAY]),
        )

        original_read_pages = SimpleRetriever._read_pages
        call_count = 0

        def read_pages_failing_twice(self, records_generator_fn, stream_slice):
            nonlocal call_count
            cursor = getattr(stream_slice, "cursor_slice", {})
            is_target = cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-01"
            if is_target:
                call_count += 1
                if call_count <= 2:
                    raise ChunkedEncodingError("simulated transient error")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_failing_twice):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    assert output.records[0].record.data["ad_group.id"] == 400003
