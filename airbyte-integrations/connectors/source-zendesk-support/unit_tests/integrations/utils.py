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
