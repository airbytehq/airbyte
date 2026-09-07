# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for source-apple-search-ads manifest.yaml.

Validates the declarative manifest structure to catch copy-paste errors
and typos in stream definitions.
"""

from pathlib import Path

import jinja2
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


def _resolve_ref(manifest, node):
    """Resolve a `$ref` pointer into the manifest, leaving other nodes untouched."""
    if not isinstance(node, dict) or "$ref" not in node:
        return node
    target = manifest
    for part in node["$ref"].lstrip("#/").split("/"):
        target = target[part]
    return target


def _get_error_handler(manifest, stream):
    return _resolve_ref(manifest, stream["retriever"]["requester"].get("error_handler", {}))


def _get_response_filters(manifest, stream):
    error_handler = _get_error_handler(manifest, stream)
    if error_handler.get("type") == "CompositeErrorHandler":
        filters = []
        for handler in error_handler.get("error_handlers", []):
            filters.extend(_resolve_ref(manifest, handler).get("response_filters", []))
        return filters
    return error_handler.get("response_filters", [])


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
        assert f.get("failure_type") == "transient_error"
        assert f.get("error_message") == "Apple Ads access token has expired."


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


ALL_STREAMS = [
    "campaigns",
    "adgroups",
    "keywords",
    "ads",
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads_report_daily",
]

REPORT_STREAMS = [
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads_report_daily",
]


def _find_filter(filters, action, http_code=None, message_contains=None):
    for f in filters:
        if f.get("action") != action:
            continue
        if http_code is not None and http_code not in f.get("http_codes", []):
            continue
        if message_contains is not None and f.get("error_message_contains") != message_contains:
            continue
        return f
    return None


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
def test_streams_share_the_error_handler_definition(manifest, stream_name):
    """Every stream must reuse a shared handler so error classification cannot drift per stream."""
    error_handler = _get_stream_def(manifest, stream_name)["retriever"]["requester"]["error_handler"]

    expected = (
        "#/definitions/error_handler_keywords_report_daily" if stream_name == "keywords_report_daily" else "#/definitions/error_handler"
    )
    assert error_handler.get("$ref") == expected, f"{stream_name} must reference {expected}"


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
def test_invalid_cert_fails_as_config_error_before_the_401_filter(manifest, stream_name):
    """Apple returns a rotated or expired signing key as a 401 with an `Invalid cert` message.
    Refreshing the token cannot fix it, so the filter must fail terminally and must be matched
    before the 401 refresh filter, since the CDK applies the first matching filter."""
    filters = _get_response_filters(manifest, _get_stream_def(manifest, stream_name))

    cert_filter = _find_filter(filters, "FAIL", message_contains="Invalid cert")
    assert cert_filter is not None, f"{stream_name} must fail on an Invalid cert response"
    assert cert_filter["failure_type"] == "config_error"

    refresh_index = next(i for i, f in enumerate(filters) if f.get("action") == "REFRESH_TOKEN_THEN_RETRY")
    assert filters.index(cert_filter) < refresh_index, "the Invalid cert filter must precede the 401 refresh filter"


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
def test_403_fails_as_config_error(manifest, stream_name):
    """A 403 is an authorization problem — the API user's role or org_id — so retrying cannot help."""
    filters = _get_response_filters(manifest, _get_stream_def(manifest, stream_name))

    forbidden = _find_filter(filters, "FAIL", http_code=403)
    assert forbidden is not None, f"{stream_name} must fail terminally on 403"
    assert forbidden["failure_type"] == "config_error"


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
@pytest.mark.parametrize("http_code", [429, 500, 502, 503, 504])
def test_rate_limit_and_server_errors_retry(manifest, stream_name, http_code):
    filters = _get_response_filters(manifest, _get_stream_def(manifest, stream_name))

    retry_filter = _find_filter(filters, "RETRY", http_code=http_code)
    assert retry_filter is not None, f"{stream_name} must retry on {http_code}"
    assert retry_filter["failure_type"] == "transient_error"


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
def test_error_handler_retries_with_exponential_backoff(manifest, stream_name):
    error_handler = _get_error_handler(manifest, _get_stream_def(manifest, stream_name))

    assert error_handler["max_retries"] == 10
    strategies = error_handler["backoff_strategies"]
    assert [s["type"] for s in strategies] == ["ExponentialBackoffStrategy"]
    assert "config.get('backoff_factor'" in strategies[0]["factor"]


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in ALL_STREAMS])
def test_error_handler_has_no_catch_all_filter(manifest, stream_name):
    """`HttpResponseFilter` predicates are evaluated against every response, including 200s, so a
    literal catch-all predicate would classify successful responses as errors. Unmatched responses
    must fall through to the CDK's terminal default instead."""
    for f in _get_response_filters(manifest, _get_stream_def(manifest, stream_name)):
        predicate = f.get("predicate")
        if predicate is None:
            assert f.get("http_codes") or f.get("error_message_contains"), f"{stream_name}: filter matches every response: {f}"
        else:
            assert predicate.strip() not in ("{{ True }}", "{{ true }}"), f"{stream_name}: catch-all predicate: {predicate}"


@pytest.mark.parametrize("stream_name", [pytest.param(name, id=name) for name in REPORT_STREAMS])
@pytest.mark.parametrize(
    "config, expected",
    [
        pytest.param({}, "P30D", id="omitted"),
        pytest.param({"lookback_window": 7}, "P7D", id="configured"),
    ],
)
def test_lookback_window_renders_a_valid_duration(manifest, stream_name, config, expected):
    """`lookback_window` is optional, and an unguarded interpolation renders `PD` when it is
    absent, which fails ISO 8601 duration parsing before any request is made."""
    incremental_sync = _get_stream_def(manifest, stream_name)["incremental_sync"]

    rendered = jinja2.Template(incremental_sync["lookback_window"]).render(config=config)
    assert rendered == expected


def test_lookback_window_spec_field(manifest):
    """Apple attributes conversions for 30 days after the fact, so the default re-reads that tail."""
    lookback_window = manifest["spec"]["connection_specification"]["properties"]["lookback_window"]

    assert lookback_window["type"] == "integer"
    assert lookback_window["default"] == 30
    assert "lookback_window" not in manifest["spec"]["connection_specification"]["required"]
