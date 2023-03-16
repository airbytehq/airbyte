#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
from datetime import datetime
from typing import Any, Mapping

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from connector_builder.message_grouper import MessageGrouper


def list_streams() -> AirbyteMessage:
    raise NotImplementedError


DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE = 5
DEFAULT_MAXIMUM_NUMBER_OF_SLICES = 5
DEFAULT_MAX_RECORDS = 100


def read_stream(source: DeclarativeSource, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog) -> AirbyteMessage:
    try:
        command_config = config.get("__test_read_config", {})
        max_pages_per_slice = command_config.get("max_pages_per_slice", DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE)
        max_slices = command_config.get("max_slices", DEFAULT_MAXIMUM_NUMBER_OF_SLICES)
        max_records = command_config.get("max_records", DEFAULT_MAX_RECORDS)
        handler = MessageGrouper(max_pages_per_slice, max_slices)
        stream_name = configured_catalog.streams[0].stream.name  # The connector builder only supports a single stream
        stream_read = handler.get_message_groups(source, config, configured_catalog, max_records)
        return AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(
            data=dataclasses.asdict(stream_read),
            stream=stream_name,
            emitted_at=_emitted_at()
        ))
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message=f"Error reading stream with config={config} and catalog={configured_catalog}")
        return error.as_airbyte_message()


def resolve_manifest(source: ManifestDeclarativeSource) -> AirbyteMessage:
    try:
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                data={"manifest": source.resolved_manifest},
                emitted_at=_emitted_at(),
                stream="resolve_manifest",
            ),
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message="Error resolving manifest.")
        return error.as_airbyte_message()


def _emitted_at():
    return int(datetime.now().timestamp()) * 1000
