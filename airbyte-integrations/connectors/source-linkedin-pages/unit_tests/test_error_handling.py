# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import time

import pytest
import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "org_id": "12345678",
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
}
_BASE_URL = "https://api.linkedin.com/rest"
_ORG_URL = f"{_BASE_URL}/organizations/12345678"


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(time, "sleep", calls.append)
    return calls


def _read_organization():
    catalog = CatalogBuilder().with_stream("organization_lookup", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def _error(output):
    assert output.errors
    return output.errors[0].trace.error


@pytest.mark.parametrize(
    "status_code, response, expected_message",
    [
        (401, {"message": "Invalid access token"}, "re-authenticate"),
        (403, {"message": "Not enough permissions"}, "ADMINISTRATOR"),
    ],
)
def test_auth_errors_are_config_errors_without_retry(status_code, response, expected_message):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_ORG_URL, status_code=status_code, json=response)
        output = _read_organization()

    error = _error(output)
    assert error.failure_type == FailureType.config_error
    assert expected_message in error.message
    if status_code == 403:
        assert "12345678" in error.message
    assert endpoint.call_count == 1


@pytest.mark.parametrize(
    "body",
    [
        {"text": "Invalid token"},
        {"json": ["Invalid token"]},
        {"json": {"message": 401}},
    ],
)
def test_auth_error_with_unexpected_body_does_not_crash(body):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_ORG_URL, status_code=401, **body)
        output = _read_organization()

    error = _error(output)
    assert error.failure_type == FailureType.config_error
    assert "re-authenticate" in error.message
    assert "{{" not in error.message
    assert endpoint.call_count == 1


def test_429_retries_and_emits_record(sleeps):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            _ORG_URL,
            [
                {"status_code": 429, "json": {"message": "Rate limit exceeded"}},
                {"status_code": 200, "json": {"id": 12345678, "localizedName": "Test Org"}},
            ],
        )
        output = _read_organization()

    assert output.records
    assert endpoint.call_count == 2
    # ExponentialBackoffStrategy factor 5: 5 * 2**1 seconds, plus the CDK's extra second.
    assert [seconds for seconds in sleeps if seconds] == [11]


def test_429_gives_up_after_five_retries(sleeps):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            _ORG_URL, status_code=429, json={"message": "Resource level throttle limit for calls to this resource is reached."}
        )
        output = _read_organization()

    error = _error(output)
    assert error.failure_type == FailureType.transient_error
    assert endpoint.call_count == 6
    assert [seconds for seconds in sleeps if seconds] == [11, 21, 41, 81, 161]


def test_retry_after_header_is_honored(sleeps):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            _ORG_URL,
            [
                {"status_code": 429, "headers": {"Retry-After": "1"}, "json": {"message": "Rate limit exceeded"}},
                {"status_code": 200, "json": {"id": 12345678, "localizedName": "Test Org"}},
            ],
        )
        output = _read_organization()

    assert output.records
    assert endpoint.call_count == 2
    # The CDK sleeps the header value plus one second; the exponential fallback would wait 10 + 1.
    assert [seconds for seconds in sleeps if seconds] == [2]


_STREAM_URLS = {
    "organization_lookup": _ORG_URL,
    "follower_statistics": f"{_BASE_URL}/organizationalEntityFollowerStatistics",
    "share_statistics": f"{_BASE_URL}/organizationalEntityShareStatistics",
    "total_follower_count": f"{_BASE_URL}/networkSizes/urn:li:organization:12345678",
    "follower_statistics_time_bound": f"{_BASE_URL}/organizationalEntityFollowerStatistics",
    "share_statistics_time_bound": f"{_BASE_URL}/organizationalEntityShareStatistics",
}


@pytest.mark.parametrize("stream_name", list(_STREAM_URLS))
@freeze_time("2026-10-23T14:37:12Z")
def test_sunset_api_version_fails_without_retry(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            _STREAM_URLS[stream_name],
            status_code=426,
            json={"status": 426, "code": "NONEXISTENT_VERSION", "message": "Requested version 20261001 is not active"},
        )
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    error = _error(output)
    assert error.failure_type == FailureType.system_error
    assert "Upgrade the source" in error.message
    assert "Requested version 20261001 is not active" in error.message
    assert endpoint.call_count == 1


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_errors_retry_and_emit_record(status_code):
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            _ORG_URL,
            [
                {"status_code": status_code, "json": {"message": "Server error"}},
                {"status_code": 200, "json": {"id": 12345678, "localizedName": "Test Org"}},
            ],
        )
        output = _read_organization()

    assert output.records
    assert endpoint.call_count == 2


@pytest.mark.parametrize(
    "linkedin_message, message_shown",
    [
        ("Invalid timeIntervals parameter [{timeGranularityType=MONTH}]", True),
        ("Invalid query parameters passed to request", False),
    ],
)
@pytest.mark.parametrize("stream_name", ["follower_statistics_time_bound", "share_statistics_time_bound"])
@freeze_time("2026-10-23T14:37:12Z")
def test_time_bound_400_is_a_system_error(stream_name, linkedin_message, message_shown):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_STREAM_URLS[stream_name], status_code=400, json={"message": linkedin_message, "status": 400})
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    error = _error(output)
    # The window never leaves what LinkedIn serves, so no 400 here is something the user can fix.
    assert error.failure_type == FailureType.system_error
    assert (linkedin_message in error.message) is message_shown
    assert endpoint.call_count == 1


def test_inactive_organization_is_a_config_error():
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_ORG_URL, status_code=404, json={"message": "Organization 12345678 is inactive", "status": 404})
        output = _read_organization()

    error = _error(output)
    assert error.failure_type == FailureType.config_error
    assert "Organization 12345678 is inactive" in error.message
    assert endpoint.call_count == 1


def test_manifest_does_not_use_composite_error_handlers():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    assert "CompositeErrorHandler" not in str(manifest)
