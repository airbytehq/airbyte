#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData


class FullRefreshStreamReader(ABC):
    @abstractmethod
    def read_stream(self, stream: Stream, cursor_field, internal_config):
        """
        Read a stream in full refresh mode
        :param stream: The stream to read data from
        :return: The stream's records
        """

    @staticmethod
    def is_record(record_data_or_message: StreamData):
        if isinstance(record_data_or_message, dict):
            return True
        elif isinstance(record_data_or_message, AirbyteMessage):
            return record_data_or_message.type == MessageType.RECORD
        else:
            return False
