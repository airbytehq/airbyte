#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, Mapping, Optional

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent.full_refresh_stream_reader import FullRefreshStreamReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig


class SyncrhonousFullRefreshReader(FullRefreshStreamReader):
    # FIXME this is duplicate from AbstractSource
    SLICE_LOG_PREFIX = "slice:"

    def read_stream(self, stream: Stream, cursor_field, logger, internal_config=InternalConfig()):
        slices = stream.generate_partitions(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field)
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        for _slice in slices:
            if self.should_log_slice_message(logger):
                yield self._create_slice_log_message(_slice)
            record_data_or_messages = stream.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
            )
            for record_data_or_message in record_data_or_messages:
                yield record_data_or_message
                if (
                    isinstance(record_data_or_message, AirbyteMessage)
                    and record_data_or_message.type == MessageType.RECORD
                    or isinstance(record_data_or_message, dict)
                ):
                    total_records_counter += 1
                    if internal_config and internal_config.limit_reached(total_records_counter):
                        return

    # FIXME duplicate
    def _create_slice_log_message(self, _slice: Optional[Mapping[str, Any]]) -> AirbyteMessage:
        """
        Mapping is an interface that can be implemented in various ways. However, json.dumps will just do a `str(<object>)` if
        the slice is a class implementing Mapping. Therefore, we want to cast this as a dict before passing this to json.dump
        """
        printable_slice = dict(_slice) if _slice else _slice
        return AirbyteMessage(
            type=MessageType.LOG,
            log=AirbyteLogMessage(level=Level.INFO, message=f"{self.SLICE_LOG_PREFIX}{json.dumps(printable_slice, default=str)}"),
        )

    # Duplicate from AbstractSource
    def should_log_slice_message(self, logger: logging.Logger):
        """

        :param logger:
        :return:
        """
        return logger.isEnabledFor(logging.DEBUG)
