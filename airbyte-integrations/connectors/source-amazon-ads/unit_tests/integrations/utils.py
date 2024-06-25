# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import operator
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_protocol.models import SyncMode
from source_amazon_ads import SourceAmazonAds
from source_amazon_ads.declarative_source_adapter import DeclarativeSourceAdapter


def read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: Dict[str, Any],
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(DeclarativeSourceAdapter(source=SourceAmazonAds()), config, catalog, state, expecting_exception)


def get_log_messages_by_log_level(logs: List[AirbyteMessage], log_level: LogLevel) -> List[str]:
    return map(operator.attrgetter("log.message"), filter(lambda x: x.log.level == log_level, logs))
