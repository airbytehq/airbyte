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
def disable_backoff_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


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
        (403, {"message": "Not enough permissions"}, "r_organization_social"),
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


def test_auth_error_with_non_json_body_does_not_crash():
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_ORG_URL, status_code=401, text="Invalid token")
        output = _read_organization()

    error = _error(output)
    assert error.failure_type == FailureType.config_error
    assert "re-authenticate" in error.message
    assert endpoint.call_count == 1


def test_429_retries_and_emits_record():
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


def test_retry_after_header_is_honored():
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


@freeze_time("2026-10-23T14:37:12Z")
def test_time_bound_400_includes_linkedin_message():
    stream_name = "follower_statistics_time_bound"
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    url = f"{_BASE_URL}/organizationalEntityFollowerStatistics"

    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(
            url,
            status_code=400,
            json={"message": "Invalid timeIntervals parameter", "status": 400},
        )
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    error = _error(output)
    assert error.failure_type == FailureType.config_error
    assert "Invalid timeIntervals parameter" in error.message
    assert endpoint.call_count == 1


def test_manifest_does_not_use_composite_error_handlers():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    assert "CompositeErrorHandler" not in str(manifest)
