#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping


class Record:
    """
    Represents a record read from a stream.
    """

    def __init__(self, data: Mapping[str, Any]):
        self.data = data

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.data == other.data
