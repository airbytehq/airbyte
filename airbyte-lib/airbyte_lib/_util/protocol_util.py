# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Internal utility functions, especially for dealing with Airbyte Protocol."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Type,
)

from airbyte_lib import exceptions as exc


if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


def airbyte_messages_to_record_dicts(
    messages: Iterable[AirbyteMessage],
) -> Iterator[dict[str, Any]]:
    """Convert an AirbyteMessage to a dictionary."""
    yield from (
        cast(dict[str, Any], airbyte_message_to_record_dict(message))
        for message in messages
        if message is not None and message.type == Type.RECORD
    )


def airbyte_message_to_record_dict(message: AirbyteMessage) -> dict[str, Any] | None:
    """Convert an AirbyteMessage to a dictionary.

    Return None if the message is not a record message.
    """
    if message.type != Type.RECORD:
        return None

    return airbyte_record_message_to_dict(message.record)


def airbyte_record_message_to_dict(
    record_message: AirbyteRecordMessage,
) -> dict[str, Any]:
    """Convert an AirbyteMessage to a dictionary.

    Return None if the message is not a record message.
    """
    result = record_message.data

    # TODO: Add the metadata columns (this breaks tests)
    # result["_airbyte_extracted_at"] = datetime.datetime.fromtimestamp(
    #     record_message.emitted_at
    # )

    return result  # noqa: RET504 # unnecessary assignment and then return (see TODO above)


def get_primary_keys_from_stream(
    stream_name: str,
    configured_catalog: ConfiguredAirbyteCatalog,
) -> set[str]:
    """Get the primary keys from a stream in the configured catalog."""
    stream = next(
        (stream for stream in configured_catalog.streams if stream.stream.name == stream_name),
        None,
    )
    if stream is None:
        raise exc.AirbyteStreamNotFoundError(
            stream_name=stream_name,
            connector_name=configured_catalog.connection.configuration["name"],
            available_streams=[stream.stream.name for stream in configured_catalog.streams],
        )

    return set(stream.stream.source_defined_primary_key or [])
