# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Iterable

from airbyte_protocol.models import AirbyteMessage, Type  # type: ignore


def filter_records(messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
    for message in messages:
        if message.type is Type.RECORD:
            yield message


def make_comparable_records(
    record_messages: Iterable[AirbyteMessage],
) -> Iterable[AirbyteMessage]:
    for message in record_messages:
        message.record.emitted_at = 0
        yield message
