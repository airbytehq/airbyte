#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.types import Record


class RecordFilter:
    def __init__(self, config, condition: str = None):
        self._config = config
        self._filter_interpolator = InterpolatedBoolean(condition)

    def filter_records(
        self,
        records: List[Record],
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> List[Record]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return [record for record in records if self._filter_interpolator.eval(self._config, record=record, **kwargs)]
