#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
from datetime import datetime
from typing import Any, List, Mapping

from airbyte_cdk.connector_builder.message_grouper import MessageGrouper
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE = 5
DEFAULT_MAXIMUM_NUMBER_OF_SLICES = 5
DEFAULT_MAXIMUM_RECORDS = 100

MAX_PAGES_PER_SLICE_KEY = "max_pages_per_slice"
MAX_SLICES_KEY = "max_slices"
MAX_RECORDS_KEY = "max_records"


@dataclasses.dataclass
class TestReadLimits:
    max_records: int = dataclasses.field(default=DEFAULT_MAXIMUM_RECORDS)
    max_pages_per_slice: int = dataclasses.field(default=DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE)
    max_slices: int = dataclasses.field(default=DEFAULT_MAXIMUM_NUMBER_OF_SLICES)


def get_limits(config: Mapping[str, Any]) -> TestReadLimits:
    command_config = config.get("__test_read_config", {})
    max_pages_per_slice = command_config.get(MAX_PAGES_PER_SLICE_KEY) or DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE
    max_slices = command_config.get(MAX_SLICES_KEY) or DEFAULT_MAXIMUM_NUMBER_OF_SLICES
    max_records = command_config.get(MAX_RECORDS_KEY) or DEFAULT_MAXIMUM_RECORDS
    return TestReadLimits(max_records, max_pages_per_slice, max_slices)


def create_source(config: Mapping[str, Any], limits: TestReadLimits) -> ManifestDeclarativeSource:
    manifest = config["__injected_declarative_manifest"]
    return ManifestDeclarativeSource(
        emit_connector_builder_messages=True,
        source_config=manifest,
        component_factory=ModelToComponentFactory(
            emit_connector_builder_messages=True,
            limit_pages_fetched_per_slice=limits.max_pages_per_slice,
            limit_slices_fetched=limits.max_slices,
            disable_retries=True,
            disable_cache=True,
        ),
    )


def read_stream(
    source: DeclarativeSource,
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    state: List[AirbyteStateMessage],
    limits: TestReadLimits,
) -> AirbyteMessage:
    try:
        handler = MessageGrouper(limits.max_pages_per_slice, limits.max_slices, limits.max_records)
        stream_name = configured_catalog.streams[0].stream.name  # The connector builder only supports a single stream
        stream_read = handler.get_message_groups(source, config, configured_catalog, state, limits.max_records)
        return AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(data=dataclasses.asdict(stream_read), stream=stream_name, emitted_at=_emitted_at()),
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(
            exc, message=filter_secrets(f"Error reading stream with config={config} and catalog={configured_catalog}: {str(exc)}")
        )
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
        error = AirbyteTracedException.from_exception(exc, message=f"Error resolving manifest: {str(exc)}")
        return error.as_airbyte_message()


def _emitted_at() -> int:
    return int(datetime.now().timestamp()) * 1000
