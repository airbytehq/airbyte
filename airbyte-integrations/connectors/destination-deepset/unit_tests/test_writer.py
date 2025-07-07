# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import secrets
from typing import Any, Mapping
from uuid import UUID, uuid4

import pytest
from destination_deepset.api import APIError, DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig, DeepsetCloudFile
from destination_deepset.writer import DeepsetCloudFileWriter

from airbyte_cdk.models import AirbyteLogMessage, AirbyteTraceMessage, Level, TraceType, Type


@pytest.fixture()
def config_dict() -> Mapping[str, Any]:
    return {
        "api_key": secrets.token_urlsafe(16),
        "base_url": "https://api.dev.cloud.dpst.dev",
        "workspace": "airbyte-test",
        "retries": 5,
    }


def test_factory(config_dict: Mapping[str, Any]) -> None:
    writer = DeepsetCloudFileWriter.factory(config_dict)

    assert isinstance(writer, DeepsetCloudFileWriter)
    assert isinstance(writer.client, DeepsetCloudApi)
    assert isinstance(writer.client.config, DeepsetCloudConfig)

    config = writer.client.config
    assert config.api_key == config_dict["api_key"]
    assert config.base_url == config_dict["base_url"]
    assert config.workspace == config_dict["workspace"]
    assert config.retries == config_dict["retries"]


def test_write_happy_path(monkeypatch: pytest.MonkeyPatch, config_dict: Mapping[str, Any], file: DeepsetCloudFile) -> None:
    writer = DeepsetCloudFileWriter.factory(config_dict)

    monkeypatch.setattr(writer.client, "upload", lambda *_, **__: uuid4())

    message = writer.write(file)
    assert message.type == Type.LOG
    assert isinstance(message.log, AirbyteLogMessage)
    assert message.log.level == Level.INFO


def test_write_returns_trace_message_if_error(
    monkeypatch: pytest.MonkeyPatch, config_dict: Mapping[str, Any], file: DeepsetCloudFile
) -> None:
    writer = DeepsetCloudFileWriter.factory(config_dict)

    def upload(*args, **kwargs) -> UUID:
        raise APIError

    monkeypatch.setattr(writer.client, "upload", upload)

    message = writer.write(file)
    assert message.type == Type.TRACE
    assert isinstance(message.trace, AirbyteTraceMessage)
    assert message.trace.type == TraceType.ERROR
