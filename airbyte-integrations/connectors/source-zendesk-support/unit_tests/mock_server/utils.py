# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import operator
from typing import Any, Dict, List, Optional

from airbyte_cdk.connector_builder.models import HttpRequest
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, SyncMode
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_parse

from ..conftest import get_source


def read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: Dict[str, Any],
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config=config, state=state), config, catalog, state, expecting_exception)


def get_log_messages_by_log_level(logs: List[AirbyteMessage], log_level: LogLevel) -> List[str]:
    return map(operator.attrgetter("log.message"), filter(lambda x: x.log.level == log_level, logs))


def datetime_to_string(dt: AirbyteDateTime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def string_to_datetime(dt_string: str) -> AirbyteDateTime:
    return ab_datetime_parse(dt_string)


def http_request_to_str(http_request: Optional[HttpRequest]) -> Optional[str]:
    if http_request is None:
        return None
    return http_request._parsed_url._replace(fragment="").geturl()


def extract_cursor_value_from_state(state_dict: Dict[str, Any], cursor_field: str = "updated_at") -> Optional[str]:
    """Extract cursor value from state dict, handling different CDK state formats.

    The CDK may emit state in different formats:
    1. Simple: {"updated_at": "123456"}
    2. Per-partition: {"state": {"updated_at": "123456"}, "states": [...], ...}
    3. Nested: {"states": [{"cursor": {"updated_at": "123456"}, ...}], ...}

    Returns the cursor value as a string, or None if not found.
    """
    # Try top-level cursor field first (simple format)
    if cursor_field in state_dict:
        return str(state_dict[cursor_field])

    # Try "state" dict (per-partition format)
    if "state" in state_dict and isinstance(state_dict["state"], dict):
        if cursor_field in state_dict["state"]:
            return str(state_dict["state"][cursor_field])

    # Try "states" list (nested format) - get the max cursor value
    if "states" in state_dict and isinstance(state_dict["states"], list) and len(state_dict["states"]) > 0:
        cursor_values = []
        for partition_state in state_dict["states"]:
            if "cursor" in partition_state and isinstance(partition_state["cursor"], dict):
                if cursor_field in partition_state["cursor"]:
                    cursor_values.append(str(partition_state["cursor"][cursor_field]))
        if cursor_values:
            # Return the max cursor value (most recent timestamp)
            return max(cursor_values, key=lambda x: int(x) if x.isdigit() else 0)

    return None


def get_partition_ids_from_state(state_dict: Dict[str, Any], partition_key: str) -> List[Any]:
    """Extract partition IDs from state dict.

    Returns a list of partition IDs for the given partition key (e.g., "post_id", "ticket_id").
    """
    partition_ids = []
    if "states" in state_dict and isinstance(state_dict["states"], list):
        for partition_state in state_dict["states"]:
            if "partition" in partition_state and isinstance(partition_state["partition"], dict):
                if partition_key in partition_state["partition"]:
                    partition_ids.append(partition_state["partition"][partition_key])
    return partition_ids
