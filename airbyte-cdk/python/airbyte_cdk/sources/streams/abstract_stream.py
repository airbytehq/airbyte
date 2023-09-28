#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Iterable

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
