#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Tests for StreamingGzipJsonDecoder — verifies streaming JSON array extraction from gzip responses."""

import gzip
import json
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from components import GzipJsonDecoder, StreamingGzipJsonDecoder


def _make_gzip_response(data: dict, chunk_size: int = 1024) -> MagicMock:
    """Create a mock response with gzipped JSON content that supports iter_content."""
    json_bytes = json.dumps(data).encode("iso-8859-1")
    compressed = gzip.compress(json_bytes)
    response = MagicMock()
    response.status_code = 200

    def iter_content(chunk_size=chunk_size):
        buf = BytesIO(compressed)
        while True:
            chunk = buf.read(chunk_size)
            if not chunk:
                break
            yield chunk

    response.iter_content = iter_content
    return response


def _make_raw_json_response(data: dict, chunk_size: int = 1024) -> MagicMock:
    """Create a mock response with raw (non-gzipped) JSON content."""
    json_bytes = json.dumps(data).encode("iso-8859-1")
    response = MagicMock()
    response.status_code = 200

    def iter_content(chunk_size=chunk_size):
        buf = BytesIO(json_bytes)
        while True:
            chunk = buf.read(chunk_size)
            if not chunk:
                break
            yield chunk

    response.iter_content = iter_content
    return response


@pytest.mark.parametrize(
    "items_field,payload,expected_records",
    [
        pytest.param(
            "dataByDepartmentAndSearchTerm",
            {
                "reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"},
                "dataByDepartmentAndSearchTerm": [
                    {"departmentName": "Electronics", "searchTerm": "laptop", "clickShare": 0.5},
                    {"departmentName": "Books", "searchTerm": "python", "clickShare": 0.3},
                ],
            },
            [
                {"departmentName": "Electronics", "searchTerm": "laptop", "clickShare": 0.5},
                {"departmentName": "Books", "searchTerm": "python", "clickShare": 0.3},
            ],
            id="search_terms_report_two_records",
        ),
        pytest.param(
            "dataByAsin",
            {
                "reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"},
                "dataByAsin": [
                    {"asin": "B001", "title": "Product A"},
                    {"asin": "B002", "title": "Product B"},
                    {"asin": "B003", "title": "Product C"},
                ],
            },
            [
                {"asin": "B001", "title": "Product A"},
                {"asin": "B002", "title": "Product B"},
                {"asin": "B003", "title": "Product C"},
            ],
            id="market_basket_report_three_records",
        ),
        pytest.param(
            "dataByAsin",
            {
                "reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"},
                "dataByAsin": [],
            },
            [{}],
            id="empty_array_yields_empty_dict",
        ),
        pytest.param(
            "dataByDepartmentAndSearchTerm",
            {
                "reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"},
                "dataByDepartmentAndSearchTerm": [
                    {"searchTerm": 'term with "quotes" and \\backslashes', "rank": 1},
                ],
            },
            [
                {"searchTerm": 'term with "quotes" and \\backslashes', "rank": 1},
            ],
            id="records_with_escaped_characters",
        ),
        pytest.param(
            "dataByAsin",
            {
                "reportSpecification": {"reportType": "TEST"},
                "dataByAsin": [
                    {"asin": "B001", "nested": {"inner": [1, 2, 3], "deep": {"value": True}}},
                ],
            },
            [
                {"asin": "B001", "nested": {"inner": [1, 2, 3], "deep": {"value": True}}},
            ],
            id="deeply_nested_record_structure",
        ),
        pytest.param(
            "nonexistentField",
            {
                "reportSpecification": {"reportType": "TEST"},
                "dataByAsin": [{"asin": "B001"}],
            },
            [{}],
            id="missing_target_field_yields_empty",
        ),
    ],
)
def test_streaming_decoder_extracts_items_from_gzip(items_field, payload, expected_records):
    """Streaming decoder correctly extracts individual array items from gzipped JSON."""
    decoder = StreamingGzipJsonDecoder(parameters={}, items_field=items_field)
    response = _make_gzip_response(payload)
    records = list(decoder.decode(response))
    assert records == expected_records


@pytest.mark.parametrize(
    "items_field,payload,expected_records",
    [
        pytest.param(
            "dataByAsin",
            {
                "reportSpecification": {"reportType": "TEST"},
                "dataByAsin": [
                    {"asin": "B001", "title": "Raw JSON Product"},
                ],
            },
            [
                {"asin": "B001", "title": "Raw JSON Product"},
            ],
            id="non_gzip_json_response",
        ),
    ],
)
def test_streaming_decoder_handles_non_gzip_response(items_field, payload, expected_records):
    """Streaming decoder falls back to raw JSON parsing when response is not gzipped."""
    decoder = StreamingGzipJsonDecoder(parameters={}, items_field=items_field)
    response = _make_raw_json_response(payload)
    records = list(decoder.decode(response))
    assert records == expected_records


def test_streaming_decoder_is_stream_response():
    """StreamingGzipJsonDecoder enables HTTP response streaming."""
    decoder = StreamingGzipJsonDecoder(parameters={}, items_field="data")
    assert decoder.is_stream_response() is True


def test_original_decoder_is_not_stream_response():
    """Original GzipJsonDecoder does NOT stream — it buffers the entire response."""
    decoder = GzipJsonDecoder(parameters={})
    assert decoder.is_stream_response() is False


def test_streaming_decoder_yields_records_incrementally():
    """Verify the decoder yields records one at a time (not all at once as a list).

    This confirms the streaming behavior — records are yielded as they're parsed,
    not after the full document is materialized in memory.
    """
    large_array = [{"id": i, "data": f"record_{i}" * 100} for i in range(1000)]
    payload = {
        "reportSpecification": {"reportType": "TEST"},
        "dataByDepartmentAndSearchTerm": large_array,
    }

    decoder = StreamingGzipJsonDecoder(parameters={}, items_field="dataByDepartmentAndSearchTerm")
    response = _make_gzip_response(payload, chunk_size=4096)

    # Consume records one at a time via the generator
    gen = decoder.decode(response)
    first_record = next(gen)
    assert first_record == {"id": 0, "data": "record_0" * 100}

    # Consume remaining and verify count
    remaining = list(gen)
    assert len(remaining) == 999
    assert remaining[-1] == {"id": 999, "data": "record_999" * 100}


def test_streaming_decoder_with_small_chunks():
    """Decoder works correctly even with very small read chunks (1 byte at a time)."""
    payload = {
        "data": [
            {"key": "value1"},
            {"key": "value2"},
        ]
    }

    decoder = StreamingGzipJsonDecoder(parameters={}, items_field="data")
    # Use tiny chunk size to stress the parser
    decoder.CHUNK_SIZE = 16
    response = _make_gzip_response(payload, chunk_size=16)
    records = list(decoder.decode(response))
    assert records == [{"key": "value1"}, {"key": "value2"}]


def test_streaming_decoder_with_key_appearing_in_string_value():
    """Decoder does not confuse the target key when it appears inside a string value."""
    payload = {
        "metadata": {"description": "This has dataByAsin in a string value"},
        "dataByAsin": [
            {"asin": "B001"},
        ],
    }

    decoder = StreamingGzipJsonDecoder(parameters={}, items_field="dataByAsin")
    response = _make_gzip_response(payload)
    records = list(decoder.decode(response))
    assert records == [{"asin": "B001"}]
