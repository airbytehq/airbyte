#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from collections.abc import Mapping
from logging import Logger
from typing import Any

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Level, Status, Type
from destination_deepset.destination import DestinationDeepset


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
