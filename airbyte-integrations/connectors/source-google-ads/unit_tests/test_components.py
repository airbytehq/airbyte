#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock, Mock

from source_google_ads.components import ClickViewHttpRequester, CustomGAQueryHttpRequester, CustomGAQuerySchemaLoader, RowsStreamingDecoder

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


class TestRowsStreamingDecoder:
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
    def _decode_all(decoder: RowsStreamingDecoder, resp: "_FakeResponse"):
        return list(decoder.decode(resp))

    def test_is_stream_response_true(self):
        d = RowsStreamingDecoder(parameters={})
        assert d.is_stream_response() is True

    def test_emits_each_row_from_single_message(self):
        """One server message with two results; delivered as a single chunk."""
        msg = {
            "results": [
                {"campaign": {"id": "1", "name": "A"}},
                {"campaign": {"id": "2", "name": "B"}},
            ],
            "fieldMask": "campaign.id,campaign.name",
        }
        raw = json.dumps(msg).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [msg["results"][0]]},
            {"results": [msg["results"][1]]},
        ]

    def test_handles_chunk_boundaries_inside_item_and_between_objects(self):
        """The object is split across arbitrary byte boundaries, including within strings."""
        msg = {
            "results": [
                {"segments": {"date": "2025-10-01"}, "metrics": {"clicks": 1}},
                {"segments": {"date": "2025-10-02"}, "metrics": {"clicks": 2}},
            ]
        }
        s = json.dumps(msg)

        # Split deliberately in awkward places (inside keys/values)
        chunks = [
            s[:23].encode(),  # '{"results": [{"segments":'
            s[23:40].encode(),  # ' {"date": "2025-10-01"'
            s[40:63].encode(),  # '}, "metrics": {"clicks": '
            s[63:65].encode(),  # '1'
            s[65:88].encode(),  # '}}, {"segments": {"date"'
            s[88:110].encode(),  # ': "2025-10-02"}, "metric'
            s[110:].encode(),  # 's": {"clicks": 2}}]}'
        ]

        resp = self._FakeResponse(chunks=chunks)
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [msg["results"][0]]},
            {"results": [msg["results"][1]]},
        ]

    def test_concatenated_messages_without_newlines(self):
        """Two top-level server messages concatenated back-to-back."""
        msg1 = {"results": [{"x": 1}]}
        msg2 = {"results": [{"x": 2}, {"x": 3}]}
        raw = (json.dumps(msg1) + json.dumps(msg2)).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [msg1["results"][0]]},
            {"results": [msg2["results"][0]]},
            {"results": [msg2["results"][1]]},
        ]

    def test_braces_inside_strings_do_not_confuse_depth(self):
        """Braces and brackets inside string values must not break item boundary tracking."""
        tricky_text = "note: has braces { like this } and [also arrays]"
        msg = {
            "results": [
                {"ad": {"id": "42"}, "desc": tricky_text},
                {"ad": {"id": "43"}, "desc": tricky_text},
            ],
            "fieldMask": "ad.id,desc",
        }
        raw = json.dumps(msg).encode("utf-8")

        # Split to ensure the string spans chunks
        resp = self._FakeResponse(chunks=[raw[:40], raw[40:120], raw[120:]])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [msg["results"][0]]},
            {"results": [msg["results"][1]]},
        ]

    def test_nested_objects_and_arrays_within_row(self):
        """A row containing nested dicts and arrays; ensures per-item depth is tracked correctly."""
        row = {
            "campaign": {"id": "9", "labels": [{"id": 1}, {"id": 2}]},
            "metrics": {"conversions": [0.1, 0.2, 0.3]},
        }
        msg = {"results": [row]}
        raw = json.dumps(msg).encode("utf-8")

        # Split across array/object boundaries
        resp = self._FakeResponse(chunks=[raw[:15], raw[15:35], raw[35:60], raw[60:]])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [{"results": [row]}]

    def test_empty_results_array_yields_nothing(self):
        msg = {"results": []}
        raw = json.dumps(msg).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == []

    def test_ignores_messages_without_results_key(self):
        msg = {"fieldMask": "whatever", "requestId": "abc"}
        raw = json.dumps(msg).encode("utf-8")

        resp = self._FakeResponse(chunks=[raw])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == []

    def test_multiple_messages_mixed_empty_and_nonempty(self):
        m1 = {"results": [{"a": 1}]}
        m2 = {"results": []}
        m3 = {"results": [{"a": 2}, {"a": 3}]}
        raw = (json.dumps(m1) + json.dumps(m2) + json.dumps(m3)).encode("utf-8")

        # Force a few smaller chunks
        resp = self._FakeResponse(chunks=[raw[:20], raw[20:55], raw[55:]])
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [m1["results"][0]]},
            {"results": [m3["results"][0]]},
            {"results": [m3["results"][1]]},
        ]

    def test_brackets_inside_strings_are_ignored_for_item_boundaries(self):
        """
        Ensure [square] and {curly} brackets that appear inside quoted strings
        do NOT affect depth tracking and that rows are emitted correctly.
        Also covers escaped quotes and backslashes inside the same strings,
        with splits across chunk boundaries.
        """
        tricky1 = r"line with [brackets] and {braces} and escaped quote \" and backslash \\"
        tricky2 = r"second line with closing brackets ]} \} \] \" \\ and , commas"

        msg = {
            "results": [
                {"ad": {"id": "101"}, "text": tricky1},
                {"ad": {"id": "102"}, "text": tricky2},
            ],
            "fieldMask": "ad.id,text",
        }
        raw = json.dumps(msg).encode("utf-8")

        # Split deliberately so the tricky strings are cut across chunk boundaries
        splits = [35, 70, 105, 160, 220, len(raw)]
        chunks = []
        start = 0
        for end in splits:
            chunks.append(raw[start:end])
            start = end

        resp = self._FakeResponse(chunks=chunks)
        d = RowsStreamingDecoder(parameters={})

        out = self._decode_all(d, resp)
        assert out == [
            {"results": [msg["results"][0]]},
            {"results": [msg["results"][1]]},
        ]
