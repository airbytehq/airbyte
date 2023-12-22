"""Internal utility functions, especially for dealing with Airbyte Protocol."""

import datetime
from typing import Any, Iterable, cast

from airbyte_protocol.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, Type

def airbyte_messages_to_record_dicts(messages: Iterable[AirbyteMessage]) -> Iterable[dict[str, Any]]:
    """Convert an AirbyteMessage to a dictionary."""
    yield from {
        cast(dict[str, Any], airbyte_message_to_record_dict(message))
        for message in messages
        if message is not None
    }


def airbyte_message_to_record_dict(message: AirbyteMessage) -> dict[str, Any] | None:
    """Convert an AirbyteMessage to a dictionary.
    
    Return None if the message is not a record message.
    """
    if not message.type == Type.RECORD:
        return None
    
    return airbyte_record_message_to_dict(message.record)

def airbyte_record_message_to_dict(record_message: AirbyteRecordMessage) -> dict[str, Any] | None:
    """Convert an AirbyteMessage to a dictionary.
    
    Return None if the message is not a record message.
    """
    result = record_message.data
    result["_airbyte_extracted_at"] = datetime.datetime.fromtimestamp(
        record_message.emitted_at
    )

    return result
