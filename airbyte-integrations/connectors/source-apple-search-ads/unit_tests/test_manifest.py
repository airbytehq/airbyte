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
STREAM_NAMES = [
    "campaigns",
    "adgroups",
    "keywords",
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads",
    "ads_report_daily",
]
REPORT_STREAM_NAMES = [
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads_report_daily",
]


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


def _resolve_ref(manifest, value):
    if isinstance(value, dict) and "$ref" in value:
        path = value["$ref"].removeprefix("#/").split("/")
        resolved = manifest
        for component in path:
            resolved = resolved[component]
        return resolved
    return value


def _get_error_handler(manifest, stream):
    handler = stream["retriever"]["requester"]["error_handler"]
    return _resolve_ref(manifest, handler)


def _get_response_filters(manifest, stream):
    error_handler = _get_error_handler(manifest, stream)
    return [_resolve_ref(manifest, response_filter) for response_filter in error_handler.get("response_filters", [])]


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
    for f in _get_response_filters(manifest, stream):
        predicate = f.get("predicate", "")
        assert "CAMPAIGN DOES NOT CONTAIN KEYWORD" not in predicate, "ads_report_daily must not contain keyword-specific error predicate"


def test_keywords_report_daily_retains_keyword_predicate(manifest):
    """keywords_report_daily must keep the keyword-specific IGNORE predicate."""
    stream = _get_stream_def(manifest, "keywords_report_daily")
    has_predicate = any("CAMPAIGN DOES NOT CONTAIN KEYWORD" in f.get("predicate", "") for f in _get_response_filters(manifest, stream))
    assert has_predicate, "keywords_report_daily must retain the keyword-specific IGNORE predicate"


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("campaigns", id="campaigns"),
        pytest.param("adgroups", id="adgroups"),
        pytest.param("keywords", id="keywords"),
        pytest.param("campaigns_report_daily", id="campaigns_report_daily"),
        pytest.param("adgroups_report_daily", id="adgroups_report_daily"),
        pytest.param("keywords_report_daily", id="keywords_report_daily"),
        pytest.param("ads", id="ads"),
        pytest.param("ads_report_daily", id="ads_report_daily"),
    ],
)
def test_streams_reactively_refresh_oauth_token_on_401(manifest, stream_name):
    """Apple Ads may return 401 before the CDK's tracked token expiry."""
    stream = _get_stream_def(manifest, stream_name)
    filters = _get_response_filters(manifest, stream)

    refresh_filters = [f for f in filters if f.get("action") == "REFRESH_TOKEN_THEN_RETRY" and 401 in f.get("http_codes", [])]

    assert refresh_filters, f"{stream_name} must reactively refresh the OAuth token and retry on 401"
    for f in refresh_filters:
        assert "Apple Ads rejected the credentials (401)" in f.get("error_message", "")


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


@pytest.mark.parametrize(
    "stream_name, expected_ref",
    [
        ("campaigns", "#/definitions/error_handler"),
        ("adgroups", "#/definitions/error_handler"),
        ("keywords", "#/definitions/error_handler"),
        ("ads", "#/definitions/error_handler"),
        ("campaigns_report_daily", "#/definitions/report_error_handler"),
        ("adgroups_report_daily", "#/definitions/report_error_handler"),
        ("keywords_report_daily", "#/definitions/keywords_report_error_handler"),
        ("ads_report_daily", "#/definitions/report_error_handler"),
    ],
)
def test_streams_use_expected_shared_error_handler(manifest, stream_name, expected_ref):
    stream = _get_stream_def(manifest, stream_name)
    assert stream["retriever"]["requester"]["error_handler"]["$ref"] == expected_ref


def test_manifest_does_not_use_composite_error_handler():
    assert "CompositeErrorHandler" not in MANIFEST_PATH.read_text()


def test_each_stream_resolves_to_default_error_handler(manifest):
    for stream_name in STREAM_NAMES:
        stream = _get_stream_def(manifest, stream_name)
        assert _get_error_handler(manifest, stream)["type"] == "DefaultErrorHandler"


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_streams_classify_api_errors(manifest, stream_name):
    filters = _get_response_filters(manifest, _get_stream_def(manifest, stream_name))
    bad_request = "config_error" if stream_name.endswith("_report_daily") else "system_error"
    for status_code, failure_type in ((400, bad_request), (403, "config_error"), (404, "system_error")):
        matching = [response_filter for response_filter in filters if status_code in response_filter.get("http_codes", [])]
        assert matching
        assert matching[0]["action"] == "FAIL"
        assert matching[0]["failure_type"] == failure_type


def test_keywords_report_daily_ignore_filter_is_first(manifest):
    filters = _get_response_filters(manifest, _get_stream_def(manifest, "keywords_report_daily"))
    assert filters[0]["action"] == "IGNORE"
    assert "CAMPAIGN DOES NOT CONTAIN KEYWORD" in filters[0]["predicate"]


def test_spec_does_not_require_optional_timezone_or_token_endpoint(manifest):
    required = manifest["spec"]["connection_specification"]["required"]
    assert "timezone" not in required
    assert "token_refresh_endpoint" not in required


def test_report_lookback_window_has_a_default(manifest):
    for stream_name in REPORT_STREAM_NAMES:
        body = _get_stream_def(manifest, stream_name)["incremental_sync"]["lookback_window"]
        assert "config.get('lookback_window', 30)" in body


def test_schemas_include_additive_campaign_and_adgroup_fields(manifest):
    campaigns = manifest["schemas"]["campaigns"]["properties"]
    adgroups = manifest["schemas"]["adgroups"]["properties"]

    assert campaigns["biddingStrategy"]["type"] == ["string", "null"]
    assert campaigns["targetCpa"]["anyOf"] == [
        {"type": "null"},
        {
            "type": "object",
            "properties": {
                "amount": {"type": "string"},
                "currency": {"type": "string"},
            },
        },
    ]
    assert adgroups["automatedKeywordsRequired"]["type"] == ["boolean", "null"]
    assert adgroups["biddingStrategy"]["type"] == ["string", "null"]
