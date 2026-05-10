# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for source-apple-search-ads manifest.yaml.

Validates the declarative manifest structure to catch copy-paste errors
and typos in stream definitions.
"""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def _get_stream_def(manifest, stream_name):
    return manifest["definitions"]["streams"][stream_name]


def _get_date_field_values(stream):
    """Extract values of all 'date' AddedFieldDefinition transformations."""
    values = []
    for t in stream.get("transformations", []):
        for field in t.get("fields", []):
            if field.get("path") == ["date"]:
                values.append(field["value"])
    return values


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("campaigns_report_daily", id="campaigns_report_daily"),
        pytest.param("adgroups_report_daily", id="adgroups_report_daily"),
        pytest.param("keywords_report_daily", id="keywords_report_daily"),
        pytest.param("ads_report_daily", id="ads_report_daily"),
    ],
)
def test_report_stream_date_field_uses_start_time(manifest, stream_name):
    """DatetimeBasedCursor produces slices with start_time/end_time keys.
    The date transformation must use stream_slice.start_time."""
    stream = _get_stream_def(manifest, stream_name)
    date_values = _get_date_field_values(stream)

    assert date_values, f"{stream_name} must have a 'date' AddedFieldDefinition"
    for val in date_values:
        assert "stream_slice.start_time" in val, f"{stream_name}: expected 'stream_slice.start_time', got: {val}"
        assert "stream_slice.start_date" not in val, f"{stream_name}: must NOT use 'stream_slice.start_date': {val}"


def test_ads_report_daily_no_keyword_error_predicate(manifest):
    """ads_report_daily must not contain the keyword-specific IGNORE
    predicate that was copy-pasted from keywords_report_daily."""
    stream = _get_stream_def(manifest, "ads_report_daily")
    error_handler = stream["retriever"]["requester"].get("error_handler", {})

    for f in error_handler.get("response_filters", []):
        predicate = f.get("predicate", "")
        assert "CAMPAIGN DOES NOT CONTAIN KEYWORD" not in predicate, "ads_report_daily must not contain keyword-specific error predicate"


def test_keywords_report_daily_retains_keyword_predicate(manifest):
    """keywords_report_daily must keep the keyword-specific IGNORE predicate."""
    stream = _get_stream_def(manifest, "keywords_report_daily")
    error_handler = stream["retriever"]["requester"].get("error_handler", {})

    has_predicate = any("CAMPAIGN DOES NOT CONTAIN KEYWORD" in f.get("predicate", "") for f in error_handler.get("response_filters", []))
    assert has_predicate, "keywords_report_daily must retain the keyword-specific IGNORE predicate"


def test_ads_report_daily_request_body_slice_keys(manifest):
    """startTime and endTime in request_body_json must use the correct
    stream_slice keys produced by DatetimeBasedCursor."""
    stream = _get_stream_def(manifest, "ads_report_daily")
    body = stream["retriever"]["requester"]["request_body_json"]

    assert "stream_slice.start_time" in body["startTime"], f"startTime should use stream_slice.start_time, got: {body['startTime']}"
    assert "stream_slice.end_time" in body["endTime"], f"endTime should use stream_slice.end_time, got: {body['endTime']}"


def test_concurrency_level_configured(manifest):
    """Concurrency must be configured to enable parallel partition processing,
    which prevents heartbeat timeouts on deeply-nested substreams like ads."""
    concurrency = manifest.get("concurrency_level")
    assert concurrency is not None, "manifest must define concurrency_level"
    assert concurrency["type"] == "ConcurrencyLevel"
    default = concurrency["default_concurrency"]
    assert (
        "config.get('num_workers'" in default or "config['num_workers']" in default
    ), f"default_concurrency must reference config num_workers, got: {default}"


def test_num_workers_spec_field(manifest):
    """The spec must expose num_workers as a configurable integer field."""
    properties = manifest["spec"]["connection_specification"]["properties"]
    assert "num_workers" in properties, "spec must define num_workers property"
    num_workers = properties["num_workers"]
    assert num_workers["type"] == "integer"
    assert num_workers["default"] == 2
    assert num_workers.get("minimum", 0) >= 1
    assert num_workers.get("maximum", 999) <= 20
