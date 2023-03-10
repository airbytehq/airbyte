#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
from datetime import datetime
from typing import Any, Mapping
from typing import Union

from airbyte_protocol.models.airbyte_protocol import ConfiguredAirbyteCatalog

from airbyte_cdk.models import AirbyteRecordMessage, AirbyteMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from connector_builder.message_grouper import MessageGrouper


def list_streams() -> AirbyteRecordMessage:
    raise NotImplementedError


def read_stream(source: DeclarativeSource, config: Mapping[str, Any]):
    command_config = config.get("__command_config")
    stream_name = command_config["stream_name"]
    max_pages_per_slice = command_config["max_pages_per_slice"]
    max_slices = command_config["max_slices"]
    max_records = command_config["max_records"]
    handler = MessageGrouper(max_pages_per_slice, max_slices)
    stream_read = handler.get_grouped_messages(source, config, stream_name, max_records)
    return AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(
        data=dataclasses.asdict(stream_read),
        stream="_test_read",
        emitted_at=_emitted_at()
    ))


def resolve_manifest(source) -> Union[AirbyteMessage, AirbyteRecordMessage]:
    try:
        return AirbyteRecordMessage(
            data={"manifest": source.resolved_manifest},
            emitted_at=_emitted_at(),
            stream="",
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message="Error resolving manifest.")
        return error.as_airbyte_message()


def _emitted_at():
    return int(datetime.now().timestamp()) * 1000
