# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the connection check on `source-pipedrive`.

The check runs against the `currencies` stream (GET /v1/currencies), which is always non-empty and
only requires the base scope, so invalid credentials fail instead of vacuously passing on an empty
`deals` recents feed.
"""

import logging

import requests_mock
from conftest import get_source

from airbyte_cdk.models import Status


_CONFIG = {"api_token": "test-token", "replication_start_date": "2017-01-25 00:00:00Z"}
_BASE_URL = "https://api.pipedrive.com"


def _run_check():
    return get_source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)


def test_check_uses_currencies_stream():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v1/currencies",
            complete_qs=False,
            json={"success": True, "data": [{"id": 1, "code": "USD", "name": "US Dollar", "active_flag": True}]},
        )
        status = _run_check()

        assert status.status == Status.SUCCEEDED
        assert [request.path for request in mocker.request_history] == ["/v1/currencies"]
        assert mocker.request_history[0].headers["x-api-token"] == "test-token"


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
        assert [request.path for request in mocker.request_history] == ["/v1/currencies"]
