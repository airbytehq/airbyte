#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import dataclass
from typing import List, Optional, Union

import dpath
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from isodate import Duration, parse_duration


@dataclass
class SnapchatMarketingDatetimeBasedCursor(DatetimeBasedCursor):
    """
    SnapchatMarketingDatetimeBasedCursor is a variant of DatetimeBasedCursor that strictly compares start and end dates.
    It ensures that the start date is always less than the end date to prevent errors.

    Inherits from:
        DatetimeBasedCursor

    Custom Methods:
        _partition_daterange: Return slices without intersections
    """

    def _partition_daterange(self, start: datetime, end: datetime, step: Union[datetime.timedelta, Duration]) -> List[StreamSlice]:
        start_field = self._partition_field_start.eval(self.config)
        end_field = self._partition_field_end.eval(self.config)
        dates = []

        while start < end:
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)

            dates.append(
                StreamSlice(
                    partition={}, cursor_slice={start_field: self._format_datetime(start), end_field: self._format_datetime(end_date)}
                )
            )

            start = next_start

        return dates


@dataclass
class AddExistingRecordFields(AddFields):
    """
    AddExistingRecordFields is specifically tailored for analytics data, addressing the limitations of the current
    AddFields solution, which only offers one option for adding fields. This class ensures that fields are only added
    if they exist in the record.

    Inherits from:
        AddFields

    Custom Methods:
        transform: Adds fields only if they exist in the record
    """

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        if config is None:
            config = {}

        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}

        for parsed_field in self._parsed_fields:
            valid_types = (parsed_field.value_type,) if parsed_field.value_type else None
            value = parsed_field.value.eval(config, valid_types=valid_types, **kwargs)

            # Check if the field path exists in the record before adding the field
            if dpath.search(record, self.parse_record_path(parsed_field.value.string)):
                dpath.new(record, parsed_field.path, value)

        return record

    @staticmethod
    def parse_record_path(path: str) -> list:
        """
        Parse the record path from the given path string.

        Args:
            path (str): The path string to parse.

        Returns:
            list: The parsed record path as a list of keys.
        """
        if "record" not in path:
            return []

        path_str = path.strip("{} ").split("record", 1)[1]
        record_path = path_str.strip("[]").replace("'", "").split("][")

        return record_path
