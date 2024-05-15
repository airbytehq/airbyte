#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class RecordFilter:
    """
    Filter applied on a list of Records

    config (Config): The user-provided configuration as specified by the source's spec
    condition (str): The string representing the predicate to filter a record. Records will be removed if evaluated to False
    """

    parameters: InitVar[Mapping[str, Any]]
    config: Config
    condition: str = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._filter_interpolator = InterpolatedBoolean(condition=self.condition, parameters=parameters)

    def filter_records(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        for record in records:
            if self._filter_interpolator.eval(self.config, record=record, **kwargs):
                yield record
