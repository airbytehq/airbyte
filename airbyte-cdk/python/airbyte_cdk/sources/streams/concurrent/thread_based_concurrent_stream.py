#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.sources.streams.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.core import StreamData


class ThreadBasedConcurrentStream(AbstractStream):
    def read(self) -> Iterable[StreamData]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        raise NotImplementedError

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        raise NotImplementedError

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        raise NotImplementedError

    @property
    def source_defined_cursor(self) -> bool:
        raise NotImplementedError

    @property
    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        # Incremental reads are not supported yet. This override should be deleted when incremental reads are supported.
        return False
