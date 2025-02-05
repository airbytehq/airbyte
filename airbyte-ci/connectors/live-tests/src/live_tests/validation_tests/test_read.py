#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from collections import defaultdict
from functools import reduce
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, Optional, Tuple

import pytest
from airbyte_protocol.models import (
    AirbyteStateMessage,
    AirbyteStateStats,
    AirbyteStateType,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    ConfiguredAirbyteCatalog,
)

from live_tests.commons.json_schema_helper import conforms_to_schema
from live_tests.commons.models import ExecutionResult
from live_tests.utils import fail_test_on_failing_execution_results, get_test_logger

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.allow_diagnostic_mode
async def test_read(
    request: "SubRequest",
    record_property: Callable,
    read_target_execution_result: ExecutionResult,
):
    """
    Verify that the read command succeeds on the target connection.

    Also makes assertions about the validity of the read command output:
    - At least one state message is emitted per stream
    - Appropriate stream status messages are emitted for each stream
    - If a primary key exists for the stream, it is present in the records emitted
    """
    has_records = False
    errors = []
    warnings = []
    fail_test_on_failing_execution_results(
        record_property,
        [read_target_execution_result],
    )
    for stream in read_target_execution_result.configured_catalog.streams:
        records = read_target_execution_result.get_records_per_stream(stream.stream.name)
        state_messages = read_target_execution_result.get_states_per_stream(stream.stream.name)
        statuses = read_target_execution_result.get_status_messages_per_stream(stream.stream.name)
        primary_key = read_target_execution_result.primary_keys_per_stream.get(stream.stream.name)

        for record in records:
            has_records = True
            if not conforms_to_schema(read_target_execution_result.get_obfuscated_types(record.record.data), stream.schema()):
                errors.append(f"A record was encountered that does not conform to the schema. stream={stream.stream.name} record={record}")
            if primary_key:
                if _extract_primary_key_value(record.dict(), primary_key) is None:
                    errors.append(
                        f"Primary key subkeys {repr(primary_key)} have null values or not present in {stream.stream.name} stream records."
                    )
            if stream.stream.name not in state_messages:
                errors.append(
                    f"At least one state message should be emitted per stream, but no state messages were emitted for {stream.stream.name}."
                )
            try:
                _validate_state_messages(
                    state_messages=state_messages[stream.stream.name], configured_catalog=read_target_execution_result.configured_catalog
                )
            except AssertionError as exc:
                warnings.append(
                    f"Invalid state message for stream {stream.stream.name}. exc={exc} state_messages={state_messages[stream.stream.name]}"
                )
            if stream.stream.name not in statuses:
                warnings.append(f"No stream statuses were emitted for stream {stream.stream.name}.")
            if not _validate_stream_statuses(
                configured_catalog=read_target_execution_result.configured_catalog, statuses=statuses[stream.stream.name]
            ):
                errors.append(f"Invalid statuses for stream {stream.stream.name}. statuses={statuses[stream.stream.name]}")
    if not has_records:
        errors.append("At least one record should be read using provided catalog.")

    if errors:
        logger = get_test_logger(request)
        for error in errors:
            logger.info(error)


def _extract_primary_key_value(record: Mapping[str, Any], primary_key: List[List[str]]) -> dict[Tuple[str], Any]:
    pk_values = {}
    for pk_path in primary_key:
        pk_value: Any = reduce(lambda data, key: data.get(key) if isinstance(data, dict) else None, pk_path, record)
        pk_values[tuple(pk_path)] = pk_value
    return pk_values


def _validate_stream_statuses(configured_catalog: ConfiguredAirbyteCatalog, statuses: List[AirbyteStreamStatusTraceMessage]):
    """Validate all statuses for all streams in the catalogs were emitted in correct order:
    1. STARTED
    2. RUNNING (can be >1)
    3. COMPLETE
    """
    stream_statuses = defaultdict(list)
    for status in statuses:
        stream_statuses[f"{status.stream_descriptor.namespace}-{status.stream_descriptor.name}"].append(status.status)

    assert set(f"{x.stream.namespace}-{x.stream.name}" for x in configured_catalog.streams) == set(
        stream_statuses
    ), "All stream must emit status"

    for stream_name, status_list in stream_statuses.items():
        assert (
            len(status_list) >= 3
        ), f"Stream `{stream_name}` statuses should be emitted in the next order: `STARTED`, `RUNNING`,... `COMPLETE`"
        assert status_list[0] == AirbyteStreamStatus.STARTED
        assert status_list[-1] == AirbyteStreamStatus.COMPLETE
        assert all(x == AirbyteStreamStatus.RUNNING for x in status_list[1:-1])


def _validate_state_messages(state_messages: List[AirbyteStateMessage], configured_catalog: ConfiguredAirbyteCatalog):
    # Ensure that at least one state message is emitted for each stream
    assert len(state_messages) >= len(
        configured_catalog.streams
    ), "At least one state message should be emitted for each configured stream."

    for state_message in state_messages:
        stream_name = state_message.stream.stream_descriptor.name
        state_type = state_message.type

        # Ensure legacy state type is not emitted anymore
        assert state_type != AirbyteStateType.LEGACY, (
            f"Ensure that statuses from the {stream_name} stream are emitted using either "
            "`STREAM` or `GLOBAL` state types, as the `LEGACY` state type is now deprecated."
        )

        # Check if stats are of the correct type and present in state message
        assert isinstance(state_message.sourceStats, AirbyteStateStats), "Source stats should be in state message."
