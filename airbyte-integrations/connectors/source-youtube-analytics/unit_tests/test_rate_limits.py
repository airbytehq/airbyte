# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for YouTube Reporting API rate-limit handling."""

import time

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_REPORT_TYPES_URL = "https://youtubereporting.googleapis.com/v1/reportTypes"
_REPORT_TYPES_CATALOG = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()
_RATE_LIMIT_BODY = {"error": {"code": 429, "message": "rate limit exceeded"}}


def _read_report_types(config):
    return read(get_source(config), config, _REPORT_TYPES_CATALOG)


def _register_token(mocker):
    mocker.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "test_access_token", "expires_in": 3600},
    )


def test_429_without_daily_quota_marker_retries_and_succeeds(config, monkeypatch, capsys):
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)

    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        report_types_mock = mocker.get(
            _REPORT_TYPES_URL,
            [
                {"status_code": 429, "json": _RATE_LIMIT_BODY},
                {"status_code": 200, "json": {"reportTypes": [{"id": "channel_basic_a3"}]}},
            ],
        )

        output = _read_report_types(config)

    assert output.records
    assert report_types_mock.call_count == 2
    assert len([wait for wait in waits if wait > 0]) == 1
    assert '"reasons":[{"type":"RATE_LIMITED"}]' in capsys.readouterr().out


def test_nested_5xx_error_code_is_retried(config, monkeypatch):
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)
    body = {"error": {"code": 500, "message": "server error"}}

    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        report_types_mock = mocker.get(
            _REPORT_TYPES_URL,
            [
                {"status_code": 500, "json": body},
                {"status_code": 200, "json": {"reportTypes": [{"id": "channel_basic_a3"}]}},
            ],
        )

        output = _read_report_types(config)

    assert output.records
    assert report_types_mock.call_count == 2
    assert len([wait for wait in waits if wait > 0]) == 1


def test_daily_quota_429_fails_without_retry(config, monkeypatch):
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)
    body = {
        "error": {
            "code": 429,
            "message": "FreeQuotaRequestsPerDayPerProject quota exhausted",
        }
    }

    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        report_types_mock = mocker.get(_REPORT_TYPES_URL, status_code=429, json=body)

        output = _read_report_types(config)

    assert not output.records
    assert report_types_mock.call_count == 1
    assert not [wait for wait in waits if wait > 0]
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.transient_error
    assert error.message == "Daily YouTube API project quota is exhausted."
