#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.utils.types import StreamData


class AbstractStream(ABC):
    @abstractmethod
    def read(
        self,
    ) -> Iterable[StreamData]:
        """
        Read a stream in full refresh mode
        :param stream: The stream to read data from
        :param cursor_field:
        :param logger:
        :param slice_logger:
        :param internal_config:
        :return: The stream's records
        """

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return casing.camel_to_snake(self.__class__.__name__)

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.streams.{self.name}")

    @staticmethod
    # FIXME: need to move this!
    def is_record(record_data_or_message: StreamData) -> bool:
        if isinstance(record_data_or_message, dict):
            return True
        elif isinstance(record_data_or_message, AirbyteMessage):
            return bool(record_data_or_message.type == MessageType.RECORD)
        else:
            return False
