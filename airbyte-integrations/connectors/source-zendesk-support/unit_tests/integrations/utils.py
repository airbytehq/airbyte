# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import operator
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from source_zendesk_support import SourceZendeskSupport

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, SyncMode
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


def read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: Dict[str, Any],
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(SourceZendeskSupport(config=config, catalog=catalog, state=state), config, catalog, state, expecting_exception)


def get_log_messages_by_log_level(logs: List[AirbyteMessage], log_level: LogLevel) -> List[str]:
    return map(operator.attrgetter("log.message"), filter(lambda x: x.log.level == log_level, logs))


def datetime_to_string(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def string_to_datetime(dt_string: str) -> datetime:
    # Handle ISO 8601 format with or without timezone
    if dt_string.endswith("Z"):
        dt_string = dt_string[:-1] + "+00:00"
    return datetime.fromisoformat(dt_string)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_duration(*, days=0, weeks=0, hours=0, minutes=0, seconds=0) -> timedelta:
    return timedelta(days=days + weeks * 7, hours=hours, minutes=minutes, seconds=seconds)
