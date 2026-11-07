# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for Aviationstack HTTP error handling."""

from unittest.mock import patch

import requests_mock
import yaml
from _helpers import _get_manifest_path, get_source

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_API = "https://api.aviationstack.com/v1/airports"
_CONFIG = {"access_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
_AIRPORT = {"id": 1, "name": "Test Airport"}


def _read(config: dict[str, str] | None = None, expecting_exception: bool = False) -> EntrypointOutput:
    """Read the full-refresh airports stream."""
    config = config if config is not None else _CONFIG
    state = StateBuilder().build()
    catalog = CatalogBuilder().with_stream("airports", SyncMode.full_refresh).build()
    return read(
        get_source(config=config, state=state),
        config,
        catalog,
        state,
        expecting_exception=expecting_exception,
    )


def test_base_requester_uses_single_default_error_handler() -> None:
    """The base requester declares the three filters on one default handler."""
    manifest_path = _get_manifest_path() / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    error_handler = manifest["definitions"]["base_requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["max_retries"] == 3
    assert [response_filter["action"] for response_filter in error_handler["response_filters"]] == [
        "IGNORE",
        "RATE_LIMITED",
        "FAIL",
    ]
    assert "CompositeErrorHandler" not in manifest_path.read_text()


def test_airports_emits_records_for_successful_response() -> None:
    """A successful airports response emits its record without errors."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_API, json={"data": [_AIRPORT]})
        output = _read()

    assert [record.record.data for record in output.records] == [_AIRPORT]
    assert not output.errors


def test_403_is_ignored_without_incomplete_status() -> None:
    """A 403 response is ignored without records, trace errors, or an incomplete stream."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_API, status_code=403, json={"error": {"code": "subscription_needed"}})
        output = _read()

    assert not output.records
    assert not output.errors
    assert AirbyteStreamStatus.INCOMPLETE not in output.get_stream_statuses("airports")
    assert mocker.call_count == 1


def test_rate_limit_429_retries_before_quota_filter() -> None:
    """A rate-limited 429 is retried and a subsequent success emits a record."""
    with requests_mock.Mocker() as mocker, patch("time.sleep"):
        mocker.get(
            _API,
            [
                {"status_code": 429, "json": {"error": {"code": "rate_limit_reached", "message": "Rate limited."}}},
                {"status_code": 200, "json": {"data": [_AIRPORT]}},
            ],
        )
        output = _read()

    assert [record.record.data for record in output.records] == [_AIRPORT]
    assert not output.errors
    assert mocker.call_count == 2


def test_usage_limit_429_fails_with_quota_message() -> None:
    """A quota-exhausted 429 fails once with the configuration error message."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _API,
            status_code=429,
            json={"error": {"code": "usage_limit_reached", "message": "Your monthly usage limit has been reached."}},
        )
        output = _read(expecting_exception=True)

    errors = [error_message.trace.error for error_message in output.errors]
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert any(
        "Aviationstack rejected the request with HTTP 429 (request quota exceeded): "
        "Your monthly usage limit has been reached." in error.message
        for error in errors
    )
    assert mocker.call_count == 1


def test_persistent_500_fails_after_max_retries() -> None:
    """A persistent 500 fails after the initial request and three retries."""
    with requests_mock.Mocker() as mocker, patch("time.sleep"):
        mocker.get(_API, status_code=500, json={"error": {"code": "internal_error"}})
        output = _read(expecting_exception=True)

    assert output.errors
    assert AirbyteStreamStatus.INCOMPLETE in output.get_stream_statuses("airports")
    assert mocker.call_count == 4
