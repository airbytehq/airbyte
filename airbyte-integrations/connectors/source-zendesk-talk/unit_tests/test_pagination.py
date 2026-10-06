# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""
Regression tests for the incremental-export pagination stop condition.

Zendesk Talk incremental exports (`call_legs`, `calls`) always return a `next_page` URL and
filter `start_time` inclusively, so once a sync catches up the paginator keeps re-requesting
`start_time=end_time` and receiving the same boundary record(s). A single call can produce
several legs sharing the same `updated_at` second, so the terminal page can hold >= 2 records.

The stream must therefore stop when a page is not full (`count < 1000`, the export page size),
not when the page holds a single record. The previous `count <= 1` condition looped forever
whenever the newest second held two or more legs (oncall #13012).
"""

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
INCREMENTAL_EXPORT_STREAMS = ["call_legs", "calls"]
PAGE_SIZE = 1000


def _stop_condition(stream_name: str) -> str:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    stream = manifest["definitions"]["streams"][stream_name]
    return stream["retriever"]["paginator"]["pagination_strategy"]["stop_condition"]


def _should_stop(stream_name: str, response: dict) -> bool:
    condition = InterpolatedBoolean(condition=_stop_condition(stream_name), parameters={})
    return condition.eval(config={}, response=response)


@pytest.mark.parametrize("stream_name", INCREMENTAL_EXPORT_STREAMS)
@pytest.mark.parametrize(
    "response, expected_stop, scenario",
    [
        ({"count": PAGE_SIZE, "next_page": "url?start_time=2"}, False, "full page -> keep paginating"),
        ({"count": 20, "next_page": "url?start_time=2"}, True, "partial page -> caught up, stop"),
        # The exact #13012 loop: two legs of one call share the newest updated_at second.
        # Zendesk returns them forever with an unchanged next_page; `count <= 1` never stopped.
        ({"count": 2, "next_page": "url?start_time=2"}, True, "two-record boundary page -> stop (regression)"),
        ({"count": 1, "next_page": "url?start_time=2"}, True, "single-record boundary page -> stop"),
        ({"count": 0, "next_page": "url?start_time=2"}, True, "empty page -> stop"),
        ({"next_page": "url?start_time=2"}, True, "missing count -> stop (safe default)"),
    ],
)
def test_incremental_export_pagination_stops_on_non_full_page(stream_name, response, expected_stop, scenario):
    assert _should_stop(stream_name, response) is expected_stop, scenario


@pytest.mark.parametrize("stream_name", INCREMENTAL_EXPORT_STREAMS)
def test_stop_condition_is_page_size_based_not_single_record(stream_name):
    # Guard against regressing to a count-based "one record left" heuristic (e.g. `count <= 1`),
    # which loops when the boundary second holds multiple legs.
    condition = _stop_condition(stream_name)
    assert "< 1000" in condition, condition
    assert "<= 1" not in condition, condition
