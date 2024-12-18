# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import secrets
from collections.abc import Mapping
from logging import Logger
from pathlib import Path
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Type
from destination_deepset.api import DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig
from destination_deepset.writer import DeepsetCloudFileWriter
from pytest import MonkeyPatch


@pytest.fixture()
def config() -> Mapping[str, Any]:
    return {
        "api_key": secrets.token_urlsafe(16),
        "base_url": "https://api.dev.cloud.dpst.dev",
        "workspace": "airbyte-test",
        "retries": 5,
    }


@pytest.fixture()
def configured_catalog() -> ConfiguredAirbyteCatalog:
    path = Path("./sample_files/configured_catalog.json")
    return ConfiguredAirbyteCatalog.parse_file(path)


@pytest.fixture()
def input_messages() -> list[AirbyteMessage]:
    with Path("./sample_files/messages.jsonl").open() as f:
        return [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage.parse_raw(line)) for line in f]


@pytest.fixture()
def logger() -> Logger:
    return Mock(spec=Logger)


@pytest.fixture()
def api_client(monkeypatch: MonkeyPatch, config: Mapping[str, Any]) -> DeepsetCloudApi:
    cloud_config = DeepsetCloudConfig.parse_obj(config)
    patched = DeepsetCloudApi(cloud_config)

    monkeypatch.setattr(patched, "health_check", lambda *_, **__: None)
    monkeypatch.setattr(patched, "upload", lambda *_, **__: uuid4())

    return patched


@pytest.fixture(autouse=True)
def _ensure_mock_api(monkeypatch: MonkeyPatch, api_client: DeepsetCloudApi) -> None:
    def factory(*args) -> DeepsetCloudFileWriter:
        return DeepsetCloudFileWriter(api_client)

    monkeypatch.setattr("destination_deepset.destination.DeepsetCloudFileWriter.factory", factory)
