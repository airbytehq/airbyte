#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.lcc.iterators.iterator import Iterator


class OnlyOnceIterator(Iterator):
    def __init__(self, **kwargs):
        pass

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [dict()]
