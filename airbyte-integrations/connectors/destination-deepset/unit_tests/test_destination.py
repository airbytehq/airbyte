# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from logging import Logger
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import Mock
from uuid import uuid4

import pytest
from destination_deepset.api import DeepsetCloudApi
from destination_deepset.destination import DestinationDeepset
from destination_deepset.writer import DeepsetCloudFileWriter

from airbyte_cdk import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Level, Status, Type


@pytest.fixture()
def configured_catalog() -> ConfiguredAirbyteCatalog:
    """A configured catalog with a single stream."""
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_unstructured",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                    source_defined_cursor=True,
                    default_cursor_field=["_ab_source_file_last_modified"],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


@pytest.fixture()
def input_messages() -> list[AirbyteMessage]:
    messages = []

    with Path("sample_files/messages.jsonl").open() as f:
        for line in f:
            data = json.loads(line)
            messages.append(
                AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        data=data["data"],
                        emitted_at=data["emitted_at"],
                        stream=data["stream"],
                    ),
                ),
            )

    return messages


@pytest.fixture()
def logger() -> Logger:
    return Mock(spec=Logger)


@pytest.fixture(autouse=True)
def _setup(monkeypatch: pytest.MonkeyPatch, client: DeepsetCloudApi) -> None:
    monkeypatch.setattr(client, "health_check", lambda *_, **__: None)
    monkeypatch.setattr(client, "upload", lambda *_, **__: uuid4())
    monkeypatch.setattr("destination_deepset.destination.DeepsetCloudFileWriter.factory", lambda *_: DeepsetCloudFileWriter(client))


def test_write(config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: list[AirbyteMessage]) -> None:
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
