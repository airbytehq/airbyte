#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.cac.checks.connection_checker import ConnectionChecker


class CheckStream(ConnectionChecker):
    def __init__(self, source):
        self._source = source

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        stream = self._source.streams(config)[0]
        print(f"stream: {stream}")
        try:
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            print(f"records: {records}")
            next(records)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to stream {stream} - {error}"
