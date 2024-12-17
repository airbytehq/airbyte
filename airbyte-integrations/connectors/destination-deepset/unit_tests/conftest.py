# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import secrets

import pytest
from destination_deepset.api import DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig, DeepsetCloudFile


@pytest.fixture()
def api_base_url() -> str:
    return "https://testserver/"


@pytest.fixture()
def workspace() -> str:
    return "airbyte-test"


@pytest.fixture()
def config(api_base_url: str, workspace: str) -> DeepsetCloudConfig:
    return DeepsetCloudConfig(api_key=secrets.token_urlsafe(16), base_url=api_base_url, workspace=workspace, retries=3)


@pytest.fixture()
def client(config: DeepsetCloudConfig) -> DeepsetCloudApi:
    return DeepsetCloudApi(config=config)


@pytest.fixture()
def file() -> DeepsetCloudFile:
    return DeepsetCloudFile(name="test.md", content="# Title\nThis is a test.", meta={})
