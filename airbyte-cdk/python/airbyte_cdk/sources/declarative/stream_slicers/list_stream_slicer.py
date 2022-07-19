#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import ast
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config


class ListStreamSlicer(StreamSlicer):
    """
    Stream slicer that iterates over the values of a list
    If slice_values is a string, then evaluate it as literal and assert the resulting literal is a list
    """

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        slice_value = stream_slice.get(self._cursor_field.eval(self._config))
        if slice_value and slice_value in self._slice_values:
            self._cursor = slice_value

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        return {self._cursor_field.eval(self._config): self._cursor} if self._cursor else None

    def request_params(self) -> Mapping[str, Any]:
        pass

    def request_headers(self) -> Mapping[str, Any]:
        pass

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        pass

    def request_body_json(self) -> Optional[Mapping]:
        pass

    def __init__(self, slice_values: Union[str, List[str]], cursor_field: Union[InterpolatedString, str], config: Config):
        if isinstance(slice_values, str):
            slice_values = ast.literal_eval(slice_values)
        if isinstance(cursor_field, str):
            cursor_field = InterpolatedString(cursor_field)
        self._cursor_field = cursor_field
        self._slice_values = slice_values
        self._config = config
        self._cursor = None

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [{self._cursor_field.eval(self._config): slice_value} for slice_value in self._slice_values]
