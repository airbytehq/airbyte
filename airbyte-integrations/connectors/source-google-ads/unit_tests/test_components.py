#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ChunkedEncodingError, StreamConsumedError
from source_google_ads.components import (
    ClickViewHttpRequester,
    CustomGAQueryHttpRequester,
    CustomGAQuerySchemaLoader,
    GoogleAdsStreamingDecoder,
)

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader

from .conftest import Obj


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
        A network break should surface as ChunkedEncodingError (not swallowed).
        Some records may already have been yielded before the error.
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
