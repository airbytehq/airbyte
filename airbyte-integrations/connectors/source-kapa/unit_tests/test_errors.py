# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import ANY

import pytest
from conftest import load_response
from test_streams import THREADS_URL, read_threads


@pytest.mark.parametrize("status_code", [404, 409])
def test_missing_or_conflicting_resource_is_ignored(config, requests_mock, status_code):
    requests_mock.get(THREADS_URL, status_code=status_code, json={"message": "Resource unavailable"})

    output = read_threads(config)

    assert output.records == []
    assert requests_mock.call_count == 1


def test_permission_error_is_not_retried(config, requests_mock):
    requests_mock.get(THREADS_URL, status_code=403, json={"message": "Insufficient permissions"})

    output = read_threads(config, expecting_exception=True)

    assert output.records == []
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    ("status_code", "error_body", "headers"),
    [
        (403, {"message": "Rate limit exceeded"}, {}),
        (429, {"message": "Too many requests"}, {"Retry-After": "1"}),
        (502, {"message": "Bad gateway"}, {}),
        (503, {"message": "Service unavailable"}, {}),
        (504, {"message": "Gateway timeout"}, {}),
    ],
)
def test_transient_error_is_retried(config, requests_mock, mocker, status_code, error_body, headers):
    sleep = mocker.patch("time.sleep")
    requests_mock.get(
        THREADS_URL,
        [
            {"status_code": status_code, "json": error_body, "headers": headers},
            {"json": load_response("threads_page_2.json")},
        ],
    )

    output = read_threads(config)

    assert len(output.records) == 1
    assert requests_mock.call_count == 2
    sleep.assert_called_with(ANY)
