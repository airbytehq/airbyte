#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


class RecordFilter:
    """
    Filter applied on a list of Records
    """

    def __init__(self, config: Config, condition: str = "", **options: Optional[Mapping[str, Any]]):
        """
        :param config: The user-provided configuration as specified by the source's spec
        :param condition: The string representing the predicate to filter a record. Records will be removed if evaluated to False
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._config = config
        self._filter_interpolator = InterpolatedBoolean(condition)
        self._options = options

    def filter_records(
        self,
        records: List[Record],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Record]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return [record for record in records if self._filter_interpolator.eval(self._config, record=record, **kwargs)]
