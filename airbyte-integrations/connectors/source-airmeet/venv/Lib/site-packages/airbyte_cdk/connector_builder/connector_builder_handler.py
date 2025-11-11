#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import asdict
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.connector_builder.test_reader import TestReader
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Type,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
    TestLimits,
)
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

MAX_PAGES_PER_SLICE_KEY = "max_pages_per_slice"
MAX_SLICES_KEY = "max_slices"
MAX_RECORDS_KEY = "max_records"
MAX_STREAMS_KEY = "max_streams"


def get_limits(config: Mapping[str, Any]) -> TestLimits:
    command_config = config.get("__test_read_config", {})
    return TestLimits(
        max_records=command_config.get(MAX_RECORDS_KEY, TestLimits.DEFAULT_MAX_RECORDS),
        max_pages_per_slice=command_config.get(
            MAX_PAGES_PER_SLICE_KEY, TestLimits.DEFAULT_MAX_PAGES_PER_SLICE
        ),
        max_slices=command_config.get(MAX_SLICES_KEY, TestLimits.DEFAULT_MAX_SLICES),
        max_streams=command_config.get(MAX_STREAMS_KEY, TestLimits.DEFAULT_MAX_STREAMS),
    )


def should_migrate_manifest(config: Mapping[str, Any]) -> bool:
    """
    Determines whether the manifest should be migrated,
    based on the presence of the "__should_migrate" key in the config.

    This flag is set by the UI.
    """
    return config.get("__should_migrate", False)


def should_normalize_manifest(config: Mapping[str, Any]) -> bool:
    """
    Check if the manifest should be normalized.
    :param config: The configuration to check
    :return: True if the manifest should be normalized, False otherwise.
    """
    return config.get("__should_normalize", False)


def create_source(
    config: Mapping[str, Any],
    limits: TestLimits | None = None,
    catalog: ConfiguredAirbyteCatalog | None = None,
    state: List[AirbyteStateMessage] | None = None,
) -> ConcurrentDeclarativeSource:
    manifest = config["__injected_declarative_manifest"]

    # We enforce a concurrency level of 1 so that the stream is processed on a single thread
    # to retain ordering for the grouping of the builder message responses.
    if "concurrency_level" in manifest:
        manifest["concurrency_level"]["default_concurrency"] = 1
    else:
        manifest["concurrency_level"] = {"type": "ConcurrencyLevel", "default_concurrency": 1}

    return ConcurrentDeclarativeSource(
        catalog=catalog,
        config=config,
        state=state,
        source_config=manifest,
        emit_connector_builder_messages=True,
        migrate_manifest=should_migrate_manifest(config),
        normalize_manifest=should_normalize_manifest(config),
        limits=limits,
    )


def read_stream(
    source: ConcurrentDeclarativeSource,
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    state: List[AirbyteStateMessage],
    limits: TestLimits,
) -> AirbyteMessage:
    try:
        test_read_handler = TestReader(
            limits.max_pages_per_slice, limits.max_slices, limits.max_records
        )
        # The connector builder only supports a single stream
        stream_name = configured_catalog.streams[0].stream.name

        stream_read = test_read_handler.run_test_read(
            source,
            config,
            configured_catalog,
            stream_name,
            state,
            limits.max_records,
        )

        return AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                data=asdict(stream_read), stream=stream_name, emitted_at=_emitted_at()
            ),
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(
            exc,
            message=filter_secrets(
                f"Error reading stream with config={config} and catalog={configured_catalog}: {str(exc)}"
            ),
        )
        return error.as_airbyte_message()


def resolve_manifest(
    source: ConcurrentDeclarativeSource,
) -> AirbyteMessage:
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
        error = AirbyteTracedException.from_exception(
            exc, message=f"Error resolving manifest: {str(exc)}"
        )
        return error.as_airbyte_message()


def full_resolve_manifest(
    source: ConcurrentDeclarativeSource, limits: TestLimits
) -> AirbyteMessage:
    try:
        manifest = {**source.resolved_manifest}
        streams = manifest.get("streams", [])
        for stream in streams:
            stream["dynamic_stream_name"] = None

        mapped_streams: Dict[str, List[Dict[str, Any]]] = {}
        for stream in source.dynamic_streams:
            generated_streams = mapped_streams.setdefault(stream["dynamic_stream_name"], [])

            if len(generated_streams) < limits.max_streams:
                generated_streams += [stream]

        for generated_streams_list in mapped_streams.values():
            streams.extend(generated_streams_list)

        manifest["streams"] = streams
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                data={"manifest": manifest},
                emitted_at=_emitted_at(),
                stream="full_resolve_manifest",
            ),
        )
    except AirbyteTracedException as exc:
        return exc.as_airbyte_message()
    except Exception as exc:
        error = AirbyteTracedException.from_exception(
            exc, message=f"Error full resolving manifest: {str(exc)}"
        )
        return error.as_airbyte_message()


def _emitted_at() -> int:
    return ab_datetime_now().to_epoch_millis()
