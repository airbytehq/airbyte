#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Unit tests for `GzipJsonStreamingItemsDecoder`.

These tests cover the streaming decoder added to fix the OOM that occurs when
syncing very large Brand Analytics reports (`GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT`
and the four other Brand Analytics streams). The legacy `GzipJsonDecoder`
buffered the full decompressed JSON document in memory, which made the
container exceed its memory limit on multi-GB reports.
"""

import gzip
import io
import json
import tracemalloc
from typing import Any, Dict, List

import pytest
from components import GzipJsonDecoder, GzipJsonStreamingItemsDecoder


class _FakeResponse:
    """Minimal stand-in for `requests.Response` exposing only `raw`."""

    def __init__(self, payload_bytes: bytes) -> None:
        self.raw = io.BytesIO(payload_bytes)
        self.content = payload_bytes
        self.status_code = 200


def _gzipped(payload: Dict[str, Any]) -> bytes:
    return gzip.compress(json.dumps(payload).encode("utf-8"))


def _build_search_terms_payload(num_records: int) -> Dict[str, Any]:
    """Build a payload that mirrors the real `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` shape."""
    return {
        "reportSpecification": {
            "reportType": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        },
        "dataByDepartmentAndSearchTerm": [
            {
                "departmentName": "Electronics",
                "searchTerm": f"search-term-{i}",
                "searchFrequencyRank": i,
                "clickedAsin": f"B0{i:08d}",
            }
            for i in range(num_records)
        ],
    }


@pytest.mark.parametrize(
    "items_field_path, payload, expected_records",
    [
        pytest.param(
            "dataByDepartmentAndSearchTerm",
            _build_search_terms_payload(3),
            _build_search_terms_payload(3)["dataByDepartmentAndSearchTerm"],
            id="search-terms-three-records",
        ),
        pytest.param(
            "dataByAsin",
            {
                "reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"},
                "dataByAsin": [
                    {"asin": "B000000001", "purchasedWith": "B000000002"},
                    {"asin": "B000000003", "purchasedWith": "B000000004"},
                ],
            },
            [
                {"asin": "B000000001", "purchasedWith": "B000000002"},
                {"asin": "B000000003", "purchasedWith": "B000000004"},
            ],
            id="market-basket-two-records",
        ),
        pytest.param(
            "dataByAsin",
            {"reportSpecification": {"reportType": "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"}, "dataByAsin": []},
            [],
            id="empty-array",
        ),
    ],
)
def test_decode_yields_each_array_item(
    items_field_path: str,
    payload: Dict[str, Any],
    expected_records: List[Dict[str, Any]],
) -> None:
    """The decoder yields every element of the configured array in order."""
    decoder = GzipJsonStreamingItemsDecoder(items_field_path=items_field_path, parameters={})
    response = _FakeResponse(_gzipped(payload))

    records = list(decoder.decode(response))

    assert records == expected_records


def test_decode_handles_uncompressed_json() -> None:
    """The decoder transparently handles an uncompressed JSON body."""
    decoder = GzipJsonStreamingItemsDecoder(items_field_path="dataByAsin", parameters={})
    payload = {"dataByAsin": [{"asin": "B000000001"}, {"asin": "B000000002"}]}
    response = _FakeResponse(json.dumps(payload).encode("utf-8"))

    records = list(decoder.decode(response))

    assert records == payload["dataByAsin"]


def test_is_stream_response_is_true() -> None:
    """`is_stream_response()` must be True so the CDK reads the body off the socket."""
    decoder = GzipJsonStreamingItemsDecoder(items_field_path="dataByAsin", parameters={})

    assert decoder.is_stream_response() is True


def test_decode_streams_records_lazily() -> None:
    """
    Records must be yielded lazily — i.e. the decoder must not consume the
    full response before producing the first record.

    We assert this by reading only the first record from the generator and
    verifying the underlying `raw` stream still has bytes left to read. With
    the legacy `GzipJsonDecoder` this is impossible because `decode()` calls
    `gzip.decompress(response.content)` upfront, which fully drains the body.
    """
    # Use a payload that compresses to comfortably more than gzip's read buffer
    # so we can observe partial consumption of `response.raw` after the first
    # record is produced. With ~50k records the gzipped body is several
    # hundred KB, which is much larger than gzip.GzipFile's default read-ahead.
    decoder = GzipJsonStreamingItemsDecoder(items_field_path="dataByDepartmentAndSearchTerm", parameters={})
    response = _FakeResponse(_gzipped(_build_search_terms_payload(num_records=50_000)))

    generator = decoder.decode(response)
    first = next(generator)

    assert first["searchTerm"] == "search-term-0"
    # The generator should not have drained the entire response body yet.
    assert response.raw.tell() < len(response.content)


def test_streaming_decoder_uses_less_memory_than_legacy_decoder() -> None:
    """
    Regression test for the OOM reported in
    [airbytehq/oncall#12143](https://github.com/airbytehq/oncall/issues/12143).

    Both decoders process the same gzipped payload but the streaming decoder
    holds at most one record in Python memory at a time, while the legacy
    decoder materializes the full document plus the parsed object tree.

    We compare peak Python heap allocations for a payload that is large
    enough to make the difference observable but small enough to run quickly
    in CI.
    """
    payload = _build_search_terms_payload(num_records=20_000)
    gzipped_body = _gzipped(payload)

    streaming_decoder = GzipJsonStreamingItemsDecoder(
        items_field_path="dataByDepartmentAndSearchTerm",
        parameters={},
    )
    legacy_decoder = GzipJsonDecoder(parameters={})

    tracemalloc.start()
    for _ in streaming_decoder.decode(_FakeResponse(gzipped_body)):
        pass
    _, streaming_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    for _ in legacy_decoder.decode(_FakeResponse(gzipped_body)):
        pass
    _, legacy_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # The streaming decoder should hold a tiny working set (one record at a time
    # plus ijson's small parse buffers) while the legacy decoder must materialize
    # the entire decompressed string AND parsed object tree. Use a conservative
    # 5x ratio to keep the test stable across Python versions and platforms.
    assert streaming_peak * 5 < legacy_peak, (
        f"Expected streaming peak ({streaming_peak} bytes) to be < 1/5 of legacy peak "
        f"({legacy_peak} bytes); got ratio {legacy_peak / max(streaming_peak, 1):.2f}x"
    )
