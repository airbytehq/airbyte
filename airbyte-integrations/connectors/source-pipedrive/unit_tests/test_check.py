# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the connection check on `source-pipedrive`.

The check runs against the `currencies` stream (GET /v1/currencies), which is
always non-empty and only requires the base scope, so invalid credentials fail
instead of vacuously passing on an empty `deals` recents feed.
"""

import logging
from pathlib import Path

import requests_mock

from airbyte_cdk.models import Status
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path / "manifest.yaml"
    return Path(__file__).parent.parent / "manifest.yaml"


_MANIFEST_PATH = _get_manifest_path()
_CONFIG = {"api_token": "test-token", "replication_start_date": "2017-01-25 00:00:00Z"}
_BASE_URL = "https://api.pipedrive.com"


def _run_check():
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    return source.check(logging.getLogger("airbyte"), _CONFIG)


def test_check_uses_currencies_stream():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v1/currencies",
            complete_qs=False,
            json={
                "success": True,
                "data": [{"id": 1, "code": "USD", "name": "US Dollar", "active_flag": True}],
            },
        )
        status = _run_check()

        assert status.status == Status.SUCCEEDED
        assert len(mocker.request_history) == 1
        request = mocker.request_history[0]
        assert request.path == "/v1/currencies"
        assert "api_token=test-token" in request.query
        assert not any(r.path == "/v1/recents" for r in mocker.request_history)


def test_check_fails_on_invalid_token():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v1/currencies",
            complete_qs=False,
            status_code=401,
            json={"success": False, "error": "unauthorized access", "errorCode": 401},
        )
        status = _run_check()

        assert status.status == Status.FAILED
