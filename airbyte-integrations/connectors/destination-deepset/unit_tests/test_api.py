# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import pytest
from destination_deepset.api import APIError, DeepsetCloudApi
from httpx import codes
from pytest_httpx import HTTPXMock


def test_health_check(client: DeepsetCloudApi, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=codes.OK)
    assert client.health_check() is None, "Health check failed!"


def test_health_check_retries_requests_until_success(client: DeepsetCloudApi, httpx_mock: HTTPXMock) -> None:
    for _ in range(client.config.retries - 1):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    httpx_mock.add_response(status_code=codes.OK)

    assert client.health_check() is None, "Health check failed!"


def test_health_check_fails_if_all_attempts_are_unsuccessful(client: DeepsetCloudApi, httpx_mock: HTTPXMock) -> None:
    for _ in range(client.config.retries):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    with pytest.raises(APIError):
        client.health_check()
