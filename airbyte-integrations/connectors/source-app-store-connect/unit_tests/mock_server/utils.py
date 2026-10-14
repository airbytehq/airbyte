# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, List, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from unit_tests.conftest import get_source

from .config import ConfigBuilder


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    config = config_builder.build()
    return read(
        get_source(config=config, state=state),
        config,
        catalog(stream_name, sync_mode),
        state,
        expecting_exception,
    )


def latest_stream_state(output: EntrypointOutput, cursor_field: str) -> Any:
    stream_state = output.state_messages[-1].state.stream.stream_state
    serialized_state = vars(stream_state)

    def find_cursor(value: Any) -> Any:
        if isinstance(value, Mapping):
            if cursor_field in value:
                return value[cursor_field]
            for nested_value in value.values():
                cursor = find_cursor(nested_value)
                if cursor is not None:
                    return cursor
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for nested_value in value:
                cursor = find_cursor(nested_value)
                if cursor is not None:
                    return cursor
        return None

    cursor = find_cursor(serialized_state)
    if cursor is None:
        raise AssertionError(f"Cursor {cursor_field!r} not found in state: {serialized_state!r}")
    return cursor
