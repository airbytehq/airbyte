# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from destination_deepset.api import APIError, DeepsetCloudApi, FileUploadError
from destination_deepset.models import DeepsetCloudFile
from httpx import codes
from pytest_httpx import HTTPXMock


def test_health_check(httpx_mock: HTTPXMock, client: DeepsetCloudApi) -> None:
    httpx_mock.add_response(json={"organization": {"workspaces": [{"name": client.config.workspace}]}})
    assert client.health_check() is None, "Health check failed!"


def test_health_check_retries_requests_until_success(httpx_mock: HTTPXMock, client: DeepsetCloudApi) -> None:
    for _ in range(client.config.retries - 1):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    httpx_mock.add_response(json={"organization": {"workspaces": [{"name": client.config.workspace}]}})

    assert client.health_check() is None, "Health check failed!"


def test_health_check_fails_if_all_attempts_are_unsuccessful(httpx_mock: HTTPXMock, client: DeepsetCloudApi) -> None:
    for _ in range(client.config.retries):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    with pytest.raises(APIError):
        client.health_check()


def test_upload(httpx_mock: HTTPXMock, client: DeepsetCloudApi, file: DeepsetCloudFile) -> None:
    httpx_mock.add_response(json={"file_id": str(uuid4())})

    file_id = client.upload(file)
    assert isinstance(file_id, UUID), "Upload did not return a valid file id."


def test_upload_retries_requests_until_success(httpx_mock: HTTPXMock, client: DeepsetCloudApi, file: DeepsetCloudFile) -> None:
    for _ in range(client.config.retries - 1):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    httpx_mock.add_response(json={"file_id": str(uuid4())})

    file_id = client.upload(file)
    assert isinstance(file_id, UUID), "Upload did not return a valid file id."


def test_upload_fails_if_all_attempts_are_unsuccessful(httpx_mock: HTTPXMock, client: DeepsetCloudApi, file: DeepsetCloudFile) -> None:
    for _ in range(client.config.retries):
        httpx_mock.add_response(status_code=codes.BAD_GATEWAY)

    with pytest.raises(FileUploadError):
        client.upload(file)


def test_upload_fails_on_missing_file_id(httpx_mock: HTTPXMock, client: DeepsetCloudApi, file: DeepsetCloudFile) -> None:
    httpx_mock.add_response(json={})

    with pytest.raises(FileUploadError):
        client.upload(file)


def test_upload_fails_on_error(httpx_mock: HTTPXMock, client: DeepsetCloudApi, file: DeepsetCloudFile) -> None:
    httpx_mock.add_exception(RuntimeError("Something failed!"))

    with pytest.raises(RuntimeError):
        client.upload(file)
