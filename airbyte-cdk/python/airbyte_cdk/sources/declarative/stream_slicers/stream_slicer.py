#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode


class StreamSlicer(ABC):
    @abstractmethod
    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        pass

    @abstractmethod
    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        pass

    @abstractmethod
    def request_params(self) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_headers(self) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        pass

    @abstractmethod
    def request_body_json(self) -> Optional[Mapping]:
        pass

    @abstractmethod
    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        pass
