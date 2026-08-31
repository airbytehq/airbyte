# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the 1.4.0 error-handling semantics in `manifest.yaml`.

Every stream composes the same three response filters:

1. IGNORE on the Gong "no results" message (previously any 404 was ignored;
   now the body must contain "found corresponding to the provided filters").
2. `auth_error_filter`: 401/403 fail immediately with `config_error` so bad
   credentials surface to the user instead of being retried.
3. `transient_error_filter`: 429 and 5xx are retried, honoring `Retry-After`.

These tests mock the `calls` endpoint and assert each path at sync time.
"""

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}

_CALLS_URL = "https://api.gong.io/v2/calls"

_CALLS_RESPONSE = {
    "calls": [{"id": "c1", "started": "2024-01-02T10:00:00Z", "isPrivate": False}],
    "records": {"totalRecords": 1, "currentPageSize": 1, "currentPageNumber": 0},
}


def _read_calls(expecting_exception: bool = False):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("calls", SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog, expecting_exception=expecting_exception)


def _error_text(output) -> str:
    return " ".join(
        (error.trace.error.message or "") + " " + (error.trace.error.internal_message or "") for error in output.errors
    )


@pytest.mark.parametrize("status_code", [401, 403])
def test_auth_error_fails_immediately_with_config_error(status_code):
    """401/403 map to a terminal `config_error` and are never retried."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_CALLS_URL, status_code=status_code, json={"errors": ["unauthorized"]})
        output = _read_calls(expecting_exception=True)

        requests_made = [r for r in mocker.request_history if r.path == "/v2/calls"]
        assert len(requests_made) == 1, f"expected no retries on {status_code}, got {len(requests_made)} requests"

    assert output.records == []
    assert output.errors, f"expected an error trace for HTTP {status_code}"
    failure_types = {error.trace.error.failure_type for error in output.errors}
    assert FailureType.config_error in failure_types, f"expected config_error for HTTP {status_code}, got {failure_types}"
    assert "unauthorized" in _error_text(output).lower(), "expected the credential guidance message in the error trace"


@pytest.mark.parametrize("status_code", [429, 500, 502, 503, 504])
def test_transient_error_is_retried_until_success(status_code):
    """429/5xx are retried (honoring Retry-After) and the sync then succeeds."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _CALLS_URL,
            [
                {"status_code": status_code, "headers": {"Retry-After": "0"}, "json": {"errors": ["try later"]}},
                {"status_code": 200, "json": _CALLS_RESPONSE},
            ],
        )
        output = _read_calls()

        requests_made = [r for r in mocker.request_history if r.path == "/v2/calls"]
        assert len(requests_made) == 2, f"expected one retry after HTTP {status_code}, got {len(requests_made)} requests"

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["c1"], f"expected the record from the retried request, got {emitted_ids}"
    assert not output.errors, f"expected a clean sync after retry, got errors: {_error_text(output)}"


def test_not_found_with_no_results_message_is_ignored():
    """A 404 whose body carries Gong's 'no results' message yields an empty, successful sync."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _CALLS_URL,
            status_code=404,
            json={"errors": ["No calls found corresponding to the provided filters"]},
        )
        output = _read_calls()

    assert output.records == []
    assert not output.errors, f"expected the 'no results' 404 to be ignored, got errors: {_error_text(output)}"


def test_not_found_without_no_results_message_is_an_error():
    """Any other 404 is no longer swallowed — the sync surfaces an error."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_CALLS_URL, status_code=404, json={"errors": ["Call no longer exists"]})
        output = _read_calls(expecting_exception=True)

    assert output.records == []
    assert output.errors, "expected an unmatched 404 to fail the sync instead of being ignored"
