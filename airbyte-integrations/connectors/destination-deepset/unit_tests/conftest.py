# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import secrets
from typing import Any, Mapping

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
def config() -> Mapping[str, Any]:
    return {
        "api_key": secrets.token_urlsafe(16),
        "base_url": "https://api.dev.cloud.dpst.dev",
        "workspace": "airbyte-test",
        "retries": 5,
    }


@pytest.fixture()
def client(config: Mapping[str, Any]) -> DeepsetCloudApi:
    return DeepsetCloudApi(config=DeepsetCloudConfig.model_validate(config))


@pytest.fixture()
def file() -> DeepsetCloudFile:
    return DeepsetCloudFile(name="test.md", content="# Title\nThis is a test.", meta={})
