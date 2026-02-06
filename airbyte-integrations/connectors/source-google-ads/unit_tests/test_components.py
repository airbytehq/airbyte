#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest
import yaml
from requests.exceptions import ChunkedEncodingError, StreamConsumedError
from source_google_ads.components import (
    REPORT_MAPPING,
    ClickViewHttpRequester,
    CustomGAQueryHttpRequester,
    CustomGAQuerySchemaLoader,
    GoogleAdsHttpRequester,
    GoogleAdsRetriever,
    GoogleAdsStreamingDecoder,
)

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader
from airbyte_cdk.sources.types import StreamSlice

from .conftest import Obj, find_stream


_MANIFEST_PATH = Path(__file__).parent.parent / "source_google_ads" / "manifest.yaml"


def _load_manifest():
    with open(_MANIFEST_PATH) as f:
        return yaml.safe_load(f)


class TestCustomGAQuerySchemaLoader:
    def test_custom_ga_query_schema_loader_returns_expected_schema(self, config_for_custom_query_tests, mocker):
        query_object = MagicMock(
            return_value={
                "campaign_budget.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
                "campaign.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
                "metrics.interaction_event_types": Obj(
                    data_type=Obj(name="ENUM"),
                    is_repeated=True,
                    enum_values=["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"],
                ),
            }
        )
        mocker.patch(
            "source_google_ads.components.CustomGAQuerySchemaLoader.google_ads_client", return_value=Obj(get_fields_metadata=query_object)
        )

        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"
        )

        schema_loader = CustomGAQuerySchemaLoader(
            config=config, query=config["custom_queries_array"][0]["query"], cursor_field="{{ False }}"
        )

        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "campaign_budget.name": {"type": ["string", "null"]},
                "campaign.name": {"type": ["string", "null"]},
                "metrics.interaction_event_types": {
                    "type": ["null", "array"],
                    "items": {"type": "string", "enum": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"]},
                },
            },
        }
        assert schema_loader.get_json_schema() == expected_schema

    def test_custom_ga_query_schema_loader_with_cursor_field_returns_expected_schema(self, config_for_custom_query_tests, mocker):
        query_object = MagicMock(
            return_value={
                "campaign_budget.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
                "campaign.name": Obj(data_type=Obj(name="STRING"), is_repeated=False),
                "metrics.interaction_event_types": Obj(
                    data_type=Obj(name="ENUM"),
                    is_repeated=True,
                    enum_values=["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"],
                ),
                "segments.date": Obj(data_type=Obj(name="DATE"), is_repeated=False),
            }
        )
        mocker.patch(
            "source_google_ads.components.CustomGAQuerySchemaLoader.google_ads_client", return_value=Obj(get_fields_metadata=query_object)
        )

        schema_loader = CustomGAQuerySchemaLoader(
            config=config_for_custom_query_tests,
            query=config_for_custom_query_tests["custom_queries_array"][0]["query"],
            cursor_field="segments.date",
        )
        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "campaign_budget.name": {"type": ["string", "null"]},
                "campaign.name": {"type": ["string", "null"]},
                "metrics.interaction_event_types": {
                    "type": ["null", "array"],
                    "items": {"type": "string", "enum": ["UNSPECIFIED", "UNKNOWN", "CLICK", "ENGAGEMENT", "VIDEO_VIEW", "NONE"]},
                },
                "segments.date": {"type": ["string", "null"], "format": "date"},
            },
        }
        assert schema_loader.get_json_schema() == expected_schema


class TestCustomGAQueryHttpRequester:
    def test_given_valid_query_returns_expected_request_body(self, config_for_custom_query_tests, requests_mock):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"
        )
        requester = CustomGAQueryHttpRequester(
            name="test_custom_ga_query_http_requester",
            parameters={
                "query": config["custom_queries_array"][0]["query"],
                "cursor_field": "{{ False }}",
            },
            config=config,
        )
        request_body = requester.get_request_body_json(stream_slice={})
        assert request_body == {"query": "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types FROM campaign_budget"}

    def test_given_valid_query_with_cursor_field_returns_expected_request_body(self, config_for_custom_query_tests, requests_mock):
        config = config_for_custom_query_tests
        config["custom_queries_array"][0]["query"] = (
            "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types, segments.date FROM campaign_budget ORDER BY segments.date ASC"
        )
        requester = CustomGAQueryHttpRequester(
            name="test_custom_ga_query_http_requester",
            parameters={
                "query": config["custom_queries_array"][0]["query"],
                "cursor_field": "segments.date",
            },
            config=config,
        )
        request_body = requester.get_request_body_json(
            stream_slice={
                "customer_id": "customers/123",
                "parent_slice": {"customer_id": "123", "parent_slice": {}},
                "start_time": "2025-07-18",
                "end_time": "2025-07-19",
            }
        )
        assert request_body == {
            "query": "SELECT campaign_budget.name, campaign.name, metrics.interaction_event_types, segments.date FROM campaign_budget WHERE segments.date BETWEEN '2025-07-18' AND '2025-07-19' ORDER BY segments.date ASC"
        }


class TestClickViewHttpRequester:
    def test_click_view_http_requester_returns_expected_request_body(self, config):
        requester = ClickViewHttpRequester(
            name="test_click_view_http_requester",
            parameters={},
            config=config,
            schema_loader=InlineSchemaLoader(
                schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "ad_group.name": {"description": "The name of the ad group.", "type": ["null", "string"]},
                        "click_view.gclid": {
                            "description": "The Google Click Identifier for tracking purposes.",
                            "type": ["null", "string"],
                        },
                        "click_view.ad_group_ad": {
                            "description": "Details of the ad in the ad group that was clicked.",
                            "type": ["null", "string"],
                        },
                        "segments.date": {"description": "The date when the click occurred.", "type": ["null", "string"], "format": "date"},
                    },
                },
                parameters={},
            ),
        )
        request_body = requester.get_request_body_json(
            stream_slice={
                "customer_id": "customers/123",
                "parent_slice": {"customer_id": "123", "parent_slice": {}},
                "start_time": "2025-07-18",
                "end_time": "2025-07-19",
            }
        )
        assert request_body == {
            "query": "SELECT ad_group.name, click_view.gclid, click_view.ad_group_ad, segments.date FROM click_view WHERE segments.date = '2025-07-18'"
        }


CONFIGS = [
    GoogleAdsStreamingDecoder(chunk_size=5, max_direct_decode_bytes=10),  # tiny chunk, tiny threshold → force streaming
    GoogleAdsStreamingDecoder(),  # huge chunk, big threshold → fast path
]


@pytest.fixture(params=CONFIGS, ids=lambda c: str(c))
def decoder(request):
    return request.param


class TestGoogleAdsStreamingDecoder:
    @dataclass
    class _FakeResponse:
        chunks: List[bytes]
        status: int = 200

        def iter_content(self, chunk_size=1):
            # Ignore chunk_size; we already control chunking via self.chunks
            for c in self.chunks:
                yield c

        def raise_for_status(self):
            if self.status >= 400:
                raise Exception(f"HTTP {self.status}")

    @staticmethod
    def _decode_all(decoder: GoogleAdsStreamingDecoder, resp: "_FakeResponse"):
        return {"results": [row for decoder_output in decoder.decode(resp) for row in decoder_output["results"]]}

    def test_is_stream_response_true(self, decoder):
        assert decoder.is_stream_response() is True

    def test_emits_each_row_from_single_message(self, decoder):
        """One server message with two results; delivered as a single chunk."""
        msg = [
            {
                "results": [
                    {"campaign": {"id": "1", "name": "A"}},
                    {"campaign": {"id": "2", "name": "B"}},
                ],
                "fieldMask": "campaign.id,campaign.name",
            }
        ]
        raw = json.dumps(msg).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])

        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_handles_chunk_boundaries_inside_item_and_between_objects(self, decoder):
        """The object is split across arbitrary byte boundaries, including within strings."""
        msg = [
            {
                "results": [
                    {"segments": {"date": "2025-10-01"}, "metrics": {"clicks": 1}},
                    {"segments": {"date": "2025-10-02"}, "metrics": {"clicks": 2}},
                ]
            }
        ]
        s = json.dumps(msg)

        # Split deliberately in awkward places (inside keys/values)
        chunks = [
            s[:27].encode(),  # '[{"results": [{"segments":'
            s[27:48].encode(),  # ' {"date": "2025-10-01"'
            s[48:73].encode(),  # '}, "metrics": {"clicks": '
            s[73:74].encode(),  # '1'
            s[74:97].encode(),  # '}}, {"segments": {"date"'
            s[97:122].encode(),  # ': "2025-10-02"}, "metric'
            s[122:].encode(),  # 's": {"clicks": 2}}]}]'
        ]

        resp = self._FakeResponse(chunks=chunks)

        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_braces_inside_strings_do_not_confuse_depth(self, decoder):
        """Braces and brackets inside string values must not break item boundary tracking."""
        tricky_text = "note: has braces { like this } and [also arrays]"
        msg = [
            {
                "results": [
                    {"ad": {"id": "42"}, "desc": tricky_text},
                    {"ad": {"id": "43"}, "desc": tricky_text},
                ],
                "fieldMask": "ad.id,desc",
            }
        ]
        raw = json.dumps(msg).encode("utf-8")

        # Split to ensure the string spans chunks
        resp = self._FakeResponse(chunks=[raw[:40], raw[40:120], raw[120:]])

        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_nested_objects_and_arrays_within_row(self, decoder):
        """A row containing nested dicts and arrays; ensures per-item depth is tracked correctly."""
        row = {
            "campaign": {"id": "9", "labels": [{"id": 1}, {"id": 2}]},
            "metrics": {"conversions": [0.1, 0.2, 0.3]},
        }
        msg = [{"results": [row]}]
        raw = json.dumps(msg).encode("utf-8")

        # Split across array/object boundaries
        resp = self._FakeResponse(chunks=[raw[:15], raw[15:35], raw[35:60], raw[60:]])

        out = self._decode_all(decoder, resp)
        assert out == msg[0]

    def test_empty_results_array_yields_nothing(self, decoder):
        msg = [{"results": []}]
        raw = json.dumps(msg).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])

        out = self._decode_all(decoder, resp)
        assert out == msg[0]

    def test_brackets_inside_strings_are_ignored_for_item_boundaries(self, decoder):
        """
        Ensure [square] and {curly} brackets that appear inside quoted strings
        do NOT affect depth tracking and that rows are emitted correctly.
        Also covers escaped quotes and backslashes inside the same strings,
        with splits across chunk boundaries.
        """
        tricky1 = r"line with [brackets] and {braces} and escaped quote \" and backslash \\"
        tricky2 = r"second line with closing brackets ]} \} \] \" \\ and , commas"

        msg = [
            {
                "results": [
                    {"ad": {"id": "101"}, "text": tricky1},
                    {"ad": {"id": "102"}, "text": tricky2},
                ],
                "fieldMask": "ad.id,text",
            }
        ]
        raw = json.dumps(msg).encode("utf-8")

        # Split deliberately so the tricky strings are cut across chunk boundaries
        splits = [35, 70, 105, 160, 220, len(raw)]
        chunks = []
        start = 0
        for end in splits:
            chunks.append(raw[start:end])
            start = end

        resp = self._FakeResponse(chunks=chunks)

        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_raises_on_unfinished_record_object(self, decoder):
        """
        Stream ends while a record object is not fully closed → must raise.
        Example: '[{"results":[{"a":1}, {"b":2'  (missing closing } ] })
        """
        truncated = b'[{"results":[{"a":1}, {"b":2'
        resp = self._FakeResponse(chunks=[truncated])

        with pytest.raises(AirbyteTracedException):
            # Force full consumption to reach EOF and trigger the strict check
            _ = list(decoder.decode(resp))

    def test_raises_on_unfinished_top_level_after_last_item_closed(self, decoder):
        """
        Even if the last item '}' closed cleanly, if the enclosing array/object
        isn't closed at EOF, we still raise.
        Example: '{"results":[{"x":1}]'  (missing final '}' )
        """
        raw = b'[{"results":[{"x":1}]'
        resp = self._FakeResponse(chunks=[raw])

        with pytest.raises(AirbyteTracedException):
            _ = list(decoder.decode(resp))

    def test_compact_json_no_spaces(self, decoder):
        msg = [{"results": [{"a": {"b": 1}}, {"a": {"b": 2}}]}]
        raw = json.dumps(msg, separators=(",", ":")).encode("utf-8")
        resp = self._FakeResponse(chunks=[raw])
        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_pretty_printed_json_with_indent_and_newlines(self, decoder):
        msg = [{"results": [{"x": [1, 2, 3], "y": {"z": "ok"}}, {"x": [], "y": {"z": "still ok"}}]}]
        raw = json.dumps(msg, indent=2).encode("utf-8")
        resp = self._FakeResponse(chunks=[raw[:10], raw[10:40], raw[40:100], raw[100:]])
        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_whitespace_and_tabs_between_tokens(self, decoder):
        msg = [{"results": [{"x": 1}, {"x": 2}]}]
        s = json.dumps(msg)
        noisy = s.replace("{", "{ \t\n").replace(":", " : \t").replace(",", " ,\n ").replace("}", " \n}")
        resp = self._FakeResponse(chunks=[noisy.encode("utf-8")])
        out = self._decode_all(decoder, resp)
        assert out == {"results": msg[0]["results"]}

    def test_midstream_chunked_encoding_error_propagates(self, decoder):
        """
        A network break (ChunkedEncodingError) should propagate from the decoder.
        The GoogleAdsRetriever handles retry logic at the connector level.
        """
        msg = [{"results": [{"i": 1}, {"i": 2}, {"i": 3}, {"i": 4}]}]
        raw = json.dumps(msg).encode("utf-8")
        splits = [len(raw) // 4, len(raw) // 2, 3 * len(raw) // 4, len(raw)]
        chunks = [raw[: splits[0]], raw[splits[0] : splits[1]], raw[splits[1] : splits[2]], raw[splits[2] :]]

        @dataclass
        class _ErroringResponse:
            parts: List[bytes]
            raise_after_index: int

            def iter_content(self, chunk_size=1):
                for idx, p in enumerate(self.parts):
                    yield p
                    if idx == self.raise_after_index:
                        raise ChunkedEncodingError("simulated midstream break")

            def raise_for_status(self):
                pass

        resp = _ErroringResponse(parts=chunks, raise_after_index=2)

        with pytest.raises(ChunkedEncodingError):
            _ = list(decoder.decode(resp))

    def test_stream_consumed_error_propagates_immediately(self, decoder):
        @dataclass
        class _AlreadyConsumedResponse:
            def iter_content(self, chunk_size=1):
                raise StreamConsumedError("already consumed")

            def raise_for_status(self):
                pass

        with pytest.raises(StreamConsumedError):
            _ = list(decoder.decode(_AlreadyConsumedResponse()))

    @dataclass
    class _BodyResponse:
        """Respects chunk_size by slicing the body bytes."""

        body: bytes
        status: int = 200

        def iter_content(self, chunk_size=1):
            for i in range(0, len(self.body), chunk_size):
                yield self.body[i : i + chunk_size]

        def raise_for_status(self):
            if self.status >= 400:
                raise Exception(f"HTTP {self.status}")

    def test_fast_path_under_threshold_uses_json_loads(self):
        """Body size == max_direct_decode_bytes - 1 - fast path is taken."""
        decoder = GoogleAdsStreamingDecoder()
        decoder.chunk_size = 1024
        decoder.max_direct_decode_bytes = 5 * 1024

        base = [{"results": [{"x": 1}]}]
        raw = json.dumps(base, separators=(",", ":")).encode()
        # pad to reach exactly the threshold
        pad_len = decoder.max_direct_decode_bytes - len(raw)
        base[0]["results"][0]["pad"] = "x" * (pad_len - 10)
        raw = json.dumps(base, separators=(",", ":")).encode()
        assert len(raw) == decoder.max_direct_decode_bytes - 1

        resp = self._BodyResponse(raw)
        with patch.object(decoder, "_parse_records_from_stream", wraps=decoder._parse_records_from_stream) as mock_stream:
            outputs = list(decoder.decode(resp))
            results = [row for batch in outputs for row in batch["results"]]
            assert results == base[0]["results"]
            mock_stream.assert_not_called()

    def test_exact_threshold_forces_streaming(self):
        """Body size == max_direct_decode_bytes - fast path is taken."""
        decoder = GoogleAdsStreamingDecoder(chunk_size=1024, max_direct_decode_bytes=5 * 1024)

        base = [{"results": [{"x": 1}]}]
        raw = json.dumps(base, separators=(",", ":")).encode()
        # pad to reach exactly the threshold
        pad_len = decoder.max_direct_decode_bytes - len(raw)
        base[0]["results"][0]["pad"] = "x" * (pad_len - 9)
        raw = json.dumps(base, separators=(",", ":")).encode()
        assert len(raw) == decoder.max_direct_decode_bytes

        resp = self._BodyResponse(raw)
        with patch.object(decoder, "_parse_records_from_stream", wraps=decoder._parse_records_from_stream) as mock_stream:
            outputs = list(decoder.decode(resp))
            results = [row for batch in outputs for row in batch["results"]]
            assert results == base[0]["results"]
            mock_stream.assert_called_once()


class TestGoogleAdsRetriever:
    def test_chunked_encoding_error_splits_slice(self):
        """
        Verify that GoogleAdsRetriever splits the slice when ChunkedEncodingError occurs.
        A 14-day slice should be split into two 7-day slices.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        call_count = 0
        slices_processed = []

        def mock_read_pages(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            stream_slice = args[1] if len(args) > 1 else kwargs.get("stream_slice")
            slices_processed.append(stream_slice)
            if call_count == 1:
                raise ChunkedEncodingError("simulated network error")
            yield MagicMock()

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-14"},
        )

        with patch.object(retriever.__class__.__bases__[0], "_read_pages", side_effect=mock_read_pages):
            records = list(retriever._read_pages(MagicMock(), stream_slice))
            assert len(records) == 2
            assert call_count == 3
            assert slices_processed[1].cursor_slice["start_time"] == "2026-01-01"
            assert slices_processed[1].cursor_slice["end_time"] == "2026-01-07"
            assert slices_processed[2].cursor_slice["start_time"] == "2026-01-08"
            assert slices_processed[2].cursor_slice["end_time"] == "2026-01-14"

    def test_chunked_encoding_error_retries_on_minimum_slice(self):
        """
        Verify that GoogleAdsRetriever retries when error occurs on minimum slice (1 day).
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        call_count = 0

        def mock_read_pages_with_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ChunkedEncodingError("simulated network error")
            yield MagicMock()

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-01"},
        )

        with patch.object(retriever.__class__.__bases__[0], "_read_pages", side_effect=mock_read_pages_with_error):
            records = list(retriever._read_pages(MagicMock(), stream_slice))
            assert len(records) == 1
            assert call_count == 3

    def test_chunked_encoding_error_raises_after_max_retries_on_minimum_slice(self):
        """
        Verify that GoogleAdsRetriever raises AirbyteTracedException after max retries on minimum slice.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        call_count = 0

        def mock_read_pages_always_fails(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ChunkedEncodingError("persistent network error")

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-01"},
        )

        with patch.object(retriever.__class__.__bases__[0], "_read_pages", side_effect=mock_read_pages_always_fails):
            with pytest.raises(AirbyteTracedException) as exc_info:
                list(retriever._read_pages(MagicMock(), stream_slice))

            assert call_count == retriever.MAX_RETRIES + 1
            assert exc_info.value.failure_type.value == "transient_error"
            assert "retries were exhausted" in exc_info.value.message

    def test_successful_request_does_not_retry(self):
        """
        Verify that GoogleAdsRetriever does not retry when the request succeeds.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        call_count = 0

        def mock_read_pages_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            yield MagicMock()
            yield MagicMock()

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-14"},
        )

        with patch.object(retriever.__class__.__bases__[0], "_read_pages", side_effect=mock_read_pages_success):
            records = list(retriever._read_pages(MagicMock(), stream_slice))
            assert len(records) == 2
            assert call_count == 1

    def test_split_slice_returns_correct_halves(self):
        """
        Verify that _split_slice correctly splits a date range in half.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-14"},
        )

        result = retriever._split_slice(stream_slice)
        assert result is not None
        first_slice, second_slice = result

        assert first_slice.cursor_slice["start_time"] == "2026-01-01"
        assert first_slice.cursor_slice["end_time"] == "2026-01-07"
        assert second_slice.cursor_slice["start_time"] == "2026-01-08"
        assert second_slice.cursor_slice["end_time"] == "2026-01-14"

    def test_split_slice_returns_none_for_single_day(self):
        """
        Verify that _split_slice returns None for a single day slice.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-01"},
        )

        result = retriever._split_slice(stream_slice)
        assert result is None

    def test_split_slice_returns_none_for_non_date_slice(self):
        """
        Verify that _split_slice returns None for slices without date fields.
        """
        retriever = GoogleAdsRetriever(
            name="test_stream",
            primary_key="id",
            requester=MagicMock(),
            record_selector=MagicMock(),
            config={},
            parameters={},
        )

        stream_slice = StreamSlice(
            partition={"customer_id": "123"},
            cursor_slice={},
        )

        result = retriever._split_slice(stream_slice)
        assert result is None


# ---- New tests: query construction and date format validation ----


def _get_manifest_stream_names():
    manifest = _load_manifest()
    names = []
    for ref in manifest.get("streams", []):
        key = ref.split("/")[-1]
        assert key.endswith("_stream")
        names.append(key[:-7])  # strip _stream
    return names


def _split_streams_by_base():
    manifest = _load_manifest()
    defs = manifest["definitions"]
    base_incremental, base_full = [], []
    for name in _get_manifest_stream_names():
        d = defs.get(f"{name}_stream", {})
        ref = d.get("$ref", "")
        if "full_refresh_stream_base" in ref:
            base_full.append(name)
        elif "incremental_stream_base" in ref or "incremental_non_manager_stream_base" in ref:
            base_incremental.append(name)
    return base_incremental, base_full


_BASE_INCREMENTAL_STREAMS, _BASE_FULL_STREAMS = _split_streams_by_base()

# Exclude special streams handled by dedicated requesters/tests
_BASE_INCREMENTAL_STREAMS = [s for s in _BASE_INCREMENTAL_STREAMS if s not in {"change_status", "click_view"}]


@pytest.mark.parametrize("stream_name", [pytest.param(s, id=s) for s in sorted(_BASE_INCREMENTAL_STREAMS)])
def test_incremental_stream_query_construction(stream_name, config):
    schemas = _load_manifest()["schemas"]

    # Get the stream from the source and use its requester to build the query
    stream = find_stream(stream_name, config)
    spg = getattr(stream, "_stream_partition_generator")
    retriever = None
    partition_factory = getattr(spg, "_partition_factory", None)
    if partition_factory is not None:
        retriever = getattr(partition_factory, "_retriever", None)
    if retriever is None:
        legacy_stream = getattr(spg, "_stream", None)
        if legacy_stream is not None:
            retriever = getattr(legacy_stream, "retriever", None)
    assert retriever is not None
    requester = getattr(retriever, "requester")

    stream_slice = StreamSlice(
        partition={"customer_id": "123", "parent_slice": {"customer_id": "456", "parent_slice": {}}},
        cursor_slice={"start_time": "2026-01-01", "end_time": "2026-01-14"},
    )

    body = requester.get_request_body_json(stream_slice=stream_slice)
    query = body["query"]

    expected_fields = list(schemas[stream_name]["properties"].keys())
    resource_name = REPORT_MAPPING.get(stream_name, stream_name)

    select_part = query.split(" FROM ")[0].replace("SELECT ", "")
    actual_fields = [f.strip() for f in select_part.split(", ")]
    assert actual_fields == expected_fields

    assert f" FROM {resource_name} " in query
    assert "WHERE segments.date BETWEEN '2026-01-01' AND '2026-01-14'" in query
    assert "ORDER BY segments.date ASC" in query


@pytest.mark.parametrize("stream_name", [pytest.param(s, id=s) for s in sorted(_BASE_FULL_STREAMS)])
def test_full_refresh_stream_query_construction(stream_name, config):
    schemas = _load_manifest()["schemas"]

    # Get the stream from the source and use its requester to build the query
    stream = find_stream(stream_name, config)
    spg = getattr(stream, "_stream_partition_generator")
    retriever = None
    partition_factory = getattr(spg, "_partition_factory", None)
    if partition_factory is not None:
        retriever = getattr(partition_factory, "_retriever", None)
    if retriever is None:
        legacy_stream = getattr(spg, "_stream", None)
        if legacy_stream is not None:
            retriever = getattr(legacy_stream, "retriever", None)
    assert retriever is not None
    requester = getattr(retriever, "requester")

    stream_slice = StreamSlice(
        partition={"customer_id": "123", "parent_slice": {"customer_id": "456", "parent_slice": {}}},
        cursor_slice={},
    )

    body = requester.get_request_body_json(stream_slice=stream_slice)
    query = body["query"]

    expected_fields = list(schemas[stream_name]["properties"].keys())
    resource_name = REPORT_MAPPING.get(stream_name, stream_name)

    select_part = query.split(" FROM ")[0].replace("SELECT ", "")
    actual_fields = [f.strip() for f in select_part.split(", ")]
    assert actual_fields == expected_fields

    assert f"FROM {resource_name}" in query
    assert "WHERE" not in query


def _resolve_incremental_sync(stream_def: dict, defs: dict):
    visited = set()
    current = stream_def
    while isinstance(current, dict):
        inc = current.get("incremental_sync")
        if inc is not None:
            return inc
        ref = current.get("$ref")
        if not ref:
            return None
        key = ref.split("/")[-1]
        if key in visited:
            return None
        visited.add(key)
        current = defs.get(key)
    return None


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param(s, id=s)
        for s in sorted(set(_split_streams_by_base()[0] + ["click_view"]))  # all incremental base + click_view
        if s != "change_status"
    ],
)
def test_custom_retriever_streams_have_expected_date_format(stream_name):
    manifest = _load_manifest()
    defs = manifest["definitions"]

    stream_def = defs.get(f"{stream_name}_stream", {})
    inc_sync = _resolve_incremental_sync(stream_def, defs)

    assert inc_sync is not None, f"Stream {stream_name} has no incremental_sync configuration"
    assert inc_sync["datetime_format"] == GoogleAdsRetriever.DATE_FORMAT
