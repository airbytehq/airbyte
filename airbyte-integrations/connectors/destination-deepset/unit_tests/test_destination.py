# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Level, Status, Type
from destination_deepset.destination import DestinationDeepset
from destination_deepset.writer import DeepsetCloudFileWriter

if TYPE_CHECKING:
    from collections.abc import Mapping

    from destination_deepset.api import DeepsetCloudApi


@pytest.fixture()
def configured_catalog() -> ConfiguredAirbyteCatalog:
    path = Path("sample_files/configured_catalog.json")
    return ConfiguredAirbyteCatalog.parse_file(path)


@pytest.fixture()
def input_messages() -> list[AirbyteMessage]:
    with Path("sample_files/messages.jsonl").open() as f:
        return [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage.parse_raw(line)) for line in f]


@pytest.fixture()
def logger() -> Logger:
    return Mock(spec=Logger)


@pytest.fixture(autouse=True)
def _setup(monkeypatch: pytest.MonkeyPatch, client: DeepsetCloudApi) -> None:
    monkeypatch.setattr(client, "health_check", lambda *_, **__: None)
    monkeypatch.setattr(client, "upload", lambda *_, **__: uuid4())
    monkeypatch.setattr(
        "destination_deepset.destination.DeepsetCloudFileWriter.factory", lambda *_: DeepsetCloudFileWriter(client)
    )


def test_write(
    config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: list[AirbyteMessage]
) -> None:
    batch_size = len(input_messages)
    assert batch_size > 0, "Number of messages should match lines in ./sample_files/messages.jsonl"

    destination = DestinationDeepset()

    results = list(destination.write(config, configured_catalog, iter(input_messages)))
    assert len(results) == batch_size
    for result in results:
        assert isinstance(result, AirbyteMessage)
        assert result.type == Type.LOG
        assert result.log.level == Level.INFO
        assert result.log.stack_trace is None


def test_check(logger: Logger, config: Mapping[str, Any]) -> None:
    destination = DestinationDeepset()
    outcome = destination.check(logger, config)
    assert outcome.status == Status.SUCCEEDED
