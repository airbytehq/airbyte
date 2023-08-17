#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


@dataclass
class RecordTransformation:
    """
    Implementations of this class define transformations that can be applied to records of a stream.
    """

    @abstractmethod
    def transform(
        self,
        record: Mapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        """
        Transform a record by adding, deleting, or mutating fields.

        :param record: The input record to be transformed
        :param config: The user-provided configuration as specified by the source's spec
        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :return: The transformed record
        """

    def __eq__(self, other: object) -> bool:
        return other.__dict__ == self.__dict__
