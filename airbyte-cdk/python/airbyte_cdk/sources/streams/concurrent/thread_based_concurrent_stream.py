#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import lru_cache
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream, FieldPath
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability
from airbyte_cdk.sources.streams.core import StreamData


class ThreadBasedConcurrentStream(AbstractStream):
    def read(self) -> Iterable[StreamData]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    def check_availability(self) -> StreamAvailability:
        raise NotImplementedError

    @property
    def primary_key(self) -> Optional[FieldPath]:
        raise NotImplementedError

    @property
    def cursor_field(self) -> Optional[str]:
        raise NotImplementedError

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        raise NotImplementedError

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        raise NotImplementedError
