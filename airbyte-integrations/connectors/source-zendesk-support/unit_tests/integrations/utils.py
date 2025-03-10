# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import operator
from typing import Any, Dict, List, Optional

import pendulum
from pendulum.datetime import DateTime
from source_zendesk_support import SourceZendeskSupport

from airbyte_cdk.connector_builder.models import HttpRequest
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


def datetime_to_string(dt: DateTime) -> str:
    return dt.format("YYYY-MM-DDTHH:mm:ss[Z]")


def string_to_datetime(dt_string: str) -> DateTime:
    return pendulum.parse(dt_string)


def http_request_to_str(http_request: Optional[HttpRequest]) -> Optional[str]:
    if http_request is None:
        return None
    return http_request._parsed_url._replace(fragment="").geturl()
