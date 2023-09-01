#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any

from airbyte_cdk.sources.streams.core import StreamData


class Record:
    def __init__(self, stream_data: StreamData):
        self.stream_data = stream_data

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.stream_data == other.stream_data
