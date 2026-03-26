#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""
Tests for account_id validation and analytics error handler behavior.

Covers:
- maxLength constraint on account_id spec field
- Analytics error handler: retries 400s with "Retry after" but fails on validation 400s
- PinterestAnalyticsBackoffStrategy behavior
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
import yaml
from components import PinterestAnalyticsBackoffStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_manifest():
    """Load the full manifest YAML."""
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)


def _load_manifest_spec_properties():
    """Load the spec properties from the manifest."""
    return _load_manifest()["spec"]["connection_specification"]["properties"]


def _load_manifest_analytics_error_handler():
    """Load the analytics error handler definition from the manifest."""
    return _load_manifest()["definitions"]["analytics_error_handler"]


# ---------------------------------------------------------------------------
# Spec-level validation: account_id maxLength
# ---------------------------------------------------------------------------


def test_account_id_spec_has_max_length():
    """The account_id field must declare maxLength: 18 to match Pinterest API limits."""
    props = _load_manifest_spec_properties()
    account_id = props["account_id"]
    assert "maxLength" in account_id, "account_id spec field is missing maxLength constraint"
    assert account_id["maxLength"] == 18, f"account_id maxLength should be 18, got {account_id['maxLength']}"


@pytest.mark.parametrize(
    "account_id,should_be_valid",
    [
        pytest.param("123456789012345678", True, id="exactly_18_chars"),
        pytest.param("1234567890", True, id="short_valid_id"),
        pytest.param("1058768331055681142", False, id="19_chars_too_long"),
        pytest.param("12345678901234567890", False, id="20_chars_too_long"),
    ],
)
def test_account_id_length_constraint(account_id, should_be_valid):
    """Verify account_id values are accepted/rejected based on the 18-char maxLength."""
    props = _load_manifest_spec_properties()
    max_length = props["account_id"]["maxLength"]
    is_valid = len(account_id) <= max_length
    assert is_valid == should_be_valid, f"account_id '{account_id}' (len={len(account_id)}) validity mismatch: " f"expected {'valid' if should_be_valid else 'invalid'}"


# ---------------------------------------------------------------------------
# Analytics error handler: manifest structure validation
# ---------------------------------------------------------------------------


def test_analytics_error_handler_has_retry_filter_for_retryable_400():
    """The analytics error handler should RETRY 400 responses containing 'Retry after'."""
    handler = _load_manifest_analytics_error_handler()
    filters = handler["response_filters"]

    retry_filters = [f for f in filters if f["action"] == "RETRY" and 400 in f.get("http_codes", [])]
    assert len(retry_filters) >= 1, "Expected at least one RETRY filter for HTTP 400"

    retry_filter = retry_filters[0]
    assert "error_message_contains" in retry_filter, "RETRY filter for 400 should use error_message_contains to match retryable errors"
    assert "Retry after" in retry_filter["error_message_contains"], "RETRY filter should match 'Retry after' in error message"


def test_analytics_error_handler_has_fail_filter_for_validation_400():
    """The analytics error handler should FAIL on 400 responses that are not retryable."""
    handler = _load_manifest_analytics_error_handler()
    filters = handler["response_filters"]

    fail_filters = [f for f in filters if f["action"] == "FAIL" and 400 in f.get("http_codes", [])]
    assert len(fail_filters) >= 1, "Expected a FAIL filter for HTTP 400 to catch deterministic validation errors"


def test_analytics_error_handler_retry_filter_comes_before_fail():
    """The RETRY filter for 400 must come before the FAIL filter so retryable errors are matched first."""
    handler = _load_manifest_analytics_error_handler()
    filters = handler["response_filters"]

    retry_index = None
    fail_index = None
    for i, f in enumerate(filters):
        if f["action"] == "RETRY" and 400 in f.get("http_codes", []):
            if retry_index is None:
                retry_index = i
        if f["action"] == "FAIL" and 400 in f.get("http_codes", []):
            if fail_index is None:
                fail_index = i

    assert retry_index is not None, "Missing RETRY filter for 400"
    assert fail_index is not None, "Missing FAIL filter for 400"
    assert retry_index < fail_index, f"RETRY filter (index {retry_index}) must come before FAIL filter (index {fail_index})"


# ---------------------------------------------------------------------------
# PinterestAnalyticsBackoffStrategy unit tests
# ---------------------------------------------------------------------------


def _make_mock_response(status_code, json_body):
    """Create a mock requests.Response with the given status code and JSON body."""
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.json.return_value = json_body
    return response


@pytest.mark.parametrize(
    "message,expected_backoff",
    [
        pytest.param("Retry after 5 seconds", 5.0, id="retry_after_5s"),
        pytest.param("Retry after 30 seconds", 30.0, id="retry_after_30s"),
        pytest.param("Retry after 120 seconds", 120.0, id="retry_after_120s"),
    ],
)
def test_backoff_strategy_extracts_retry_after(message, expected_backoff):
    """The backoff strategy should extract wait time from 'Retry after N seconds' messages."""
    strategy = PinterestAnalyticsBackoffStrategy()
    response = _make_mock_response(400, {"message": message})
    assert strategy.backoff_time(response, attempt_count=1) == expected_backoff


@pytest.mark.parametrize(
    "message,attempt_count",
    [
        pytest.param("ad_account_id is too long. The maximum length is 18 characters.", 1, id="validation_error"),
        pytest.param("Bad request", 1, id="generic_bad_request"),
        pytest.param("Invalid parameter value", 2, id="invalid_parameter"),
    ],
)
def test_backoff_strategy_uses_exponential_for_non_retryable(message, attempt_count):
    """For messages without 'Retry after', the strategy should use exponential backoff."""
    strategy = PinterestAnalyticsBackoffStrategy()
    response = _make_mock_response(400, {"message": message})
    expected = min(2**attempt_count, 120.0)
    assert strategy.backoff_time(response, attempt_count=attempt_count) == expected
