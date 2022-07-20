#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


class RecordTransformation(ABC):
    """
    Implementations of this class define transformations that can be applied to records of a stream.
    """

    @abstractmethod
    def transform(
        self, record: Mapping[str, Any], config: Config = None, stream_state: StreamState = None, stream_slice: StreamSlice = None
    ) -> Mapping[str, Any]:
        """
        :param record: the input record to be transformed
        :return: the transformed record
        """

    def __eq__(self, other):
        return other.__dict__ == self.__dict__
