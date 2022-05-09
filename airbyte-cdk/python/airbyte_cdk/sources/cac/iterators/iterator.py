#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode

if TYPE_CHECKING:
    pass


class Iterator(ABC):
    @abstractmethod
    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        pass
