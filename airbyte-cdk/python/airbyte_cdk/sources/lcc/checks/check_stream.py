#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.lcc.checks.connection_checker import ConnectionChecker


class CheckStream(ConnectionChecker):
    def __init__(self, source: AbstractSource):
        self._source = source

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        stream = self._source.streams(config)[0]
        try:
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to stream {stream} - {error}"
