#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent.full_refresh_stream_reader import FullRefreshStreamReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message


class SyncrhonousFullRefreshReader(FullRefreshStreamReader):
    # FIXME this is duplicate from AbstractSource
    SLICE_LOG_PREFIX = "slice:"

    def read_stream(self, stream: Stream, cursor_field, internal_config, logger):
        slices = stream.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field)
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
                message = self._get_message(record_data_or_message, stream)
                yield message
                if message.type == MessageType.RECORD:
                    total_records_counter += 1
                    if internal_config.limit_reached(total_records_counter):
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

    # FIXME Duplicate from AbstractSource
    def _get_message(self, record_data_or_message: Union[StreamData, AirbyteMessage], stream: Stream):
        """
        Converts the input to an AirbyteMessage if it is a StreamData. Returns the input as is if it is already an AirbyteMessage
        """
        if isinstance(record_data_or_message, AirbyteMessage):
            return record_data_or_message
        else:
            return stream_data_to_airbyte_message(stream.name, record_data_or_message, stream.transformer, stream.get_json_schema())

    # Duplicate from AbstractSource
    def should_log_slice_message(self, logger: logging.Logger):
        """

        :param logger:
        :return:
        """
        return logger.isEnabledFor(logging.DEBUG)
