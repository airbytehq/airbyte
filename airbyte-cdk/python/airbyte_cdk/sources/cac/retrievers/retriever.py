#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.models import SyncMode


class Retriever(ABC):
    @abstractmethod
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        pass

    # FIXME: this method is only needed for the adapter
    @abstractmethod
    def stream_slices(self, *, sync_mode: SyncMode, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        pass
