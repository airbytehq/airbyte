#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod

from airbyte_cdk.sources.streams import Stream


class FullRefreshStreamReader(ABC):
    @abstractmethod
    def read_stream(self, stream: Stream, cursor_field, internal_config):
        """
        Read a stream in full refresh mode
        :param stream: The stream to read data from
        :return: The stream's records
        """
