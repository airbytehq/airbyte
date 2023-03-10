#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
from datetime import datetime
from typing import Any, Mapping

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from connector_builder.message_grouper import MessageGrouper


def list_streams() -> AirbyteMessage:
    raise NotImplementedError


def read_stream(source: DeclarativeSource, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog) -> AirbyteMessage:
    command_config = config.get("__test_read_config")
    max_pages_per_slice = command_config["max_pages_per_slice"]
    max_slices = command_config["max_slices"]
    max_records = command_config["max_records"]
    handler = MessageGrouper(max_pages_per_slice, max_slices)
    stream_read = handler.get_message_groups(source, config, configured_catalog, max_records)
    return AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(
        data=dataclasses.asdict(stream_read),
        stream="_test_read",
        emitted_at=_emitted_at()
    ))


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


CONNECTOR_BUILDER_STREAMS= {
    "resolve_manifest",
    "list_streams"
}


def is_connector_builder_request(config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog):
    stream_names = set([s.stream.name for s in configured_catalog.streams])
    if any([s in CONNECTOR_BUILDER_STREAMS for s in stream_names]) or "__test_read_config" in config:
        if len(stream_names) != 1:
            raise ValueError(f"Only reading from a single stream is supported. Got: {stream_names}")
        return True
    else:
        return False


def _emitted_at():
    return int(datetime.now().timestamp()) * 1000
