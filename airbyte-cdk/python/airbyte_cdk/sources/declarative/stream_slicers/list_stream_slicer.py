#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import ast
from typing import Any, Iterable, List, Mapping, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config


class ListStreamSlicer(StreamSlicer):
    """
    Stream slicer that iterates over the values of a list
    If slice_values is a string, then evaluate it as literal and assert the resulting literal is a list
    """

    def __init__(self, slice_values: Union[str, List[str]], slice_definition: Mapping[str, Any], config: Config):
        if isinstance(slice_values, str):
            slice_values = ast.literal_eval(slice_values)
        assert isinstance(slice_values, list)
        self._interpolation = InterpolatedMapping(slice_definition, JinjaInterpolation())
        self._slice_values = slice_values
        self._config = config

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [self._interpolation.eval(self._config, slice_value=slice_value) for slice_value in self._slice_values]
