#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor


@dataclass
class RechargeDateTimeBasedCursor(DatetimeBasedCursor):
    """
    Override for the default `DatetimeBasedCursor` to make self.close_slice() to produce `min` value instead of `max` value.
    
    This is the ONLY CHANGE MADE HERE, to make the SOURCE STATE proccessed correctly:
        The `min` value should be determined, in the first place, since we would skip the records,
        if they are updated manually, by the Customer, and the range in not AFTER the STATE value, but before.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters=parameters)

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        last_record_cursor_value = most_recent_record.get(self.cursor_field.eval(self.config)) if most_recent_record else None
        stream_slice_value_end = stream_slice.get(self.partition_field_end.eval(self.config))
        cursor_value_str_by_cursor_value_datetime = dict(
            map(
                lambda datetime_str: (self.parse_date(datetime_str), datetime_str),
                filter(lambda item: item, [self._cursor, last_record_cursor_value, stream_slice_value_end]),
            )
        )
        self._cursor = (
            cursor_value_str_by_cursor_value_datetime[min(cursor_value_str_by_cursor_value_datetime.keys())]
            if cursor_value_str_by_cursor_value_datetime
            else None
        )
