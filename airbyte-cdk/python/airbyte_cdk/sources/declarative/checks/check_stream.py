#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.source import Source


class CheckStream(ConnectionChecker):
    """
    Checks the connections by trying to read records from one or many of the streams
    """

    def __init__(self, stream_names: List[str]):
        self._stream_names = set(stream_names)

    def check_connection(self, source: Source, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        for stream in source.streams(config):
            if stream.name in self._stream_names:
                try:
                    records = stream.read_records(sync_mode=SyncMode.full_refresh)
                    next(records)
                except Exception as error:
                    return False, f"Unable to connect to stream {stream} - {error}"
        return True, None
