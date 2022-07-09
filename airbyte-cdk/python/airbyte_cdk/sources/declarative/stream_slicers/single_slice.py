#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


class SingleSlice(StreamSlicer):
    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]]):
        pass

    def set_state(self, stream_state: Mapping[str, Any]):
        pass

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self) -> Mapping[str, Any]:
        return {}

    def request_headers(self) -> Mapping[str, Any]:
        return {}

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return {}

    def request_body_json(self) -> Optional[Mapping]:
        return {}

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [dict()]
