#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import TYPE_CHECKING, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.cac.checks.connection_checker import ConnectionChecker

if TYPE_CHECKING:
    pass


class CheckStream(ConnectionChecker):
    def __init__(self, stream, vars=None, config=None):
        self._stream = stream
        self._vars = vars
        self._config = config

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            records = self._stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to stream {self._stream} - {error}"
