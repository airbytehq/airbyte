#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class RechargeDateTimeBasedCursor(DatetimeBasedCursor):
    """
    Override for the default `DatetimeBasedCursor` to make self.close_slice() to produce `min` value instead of `max` value.

    Override for the `close_slice()` - to make the SOURCE STATE proccessed correctly:
        The `min` value should be determined, in the first place, since we would skip the records,
        if they are updated manually, by the Customer, and the range in not AFTER the STATE value, but before.

    Override for the `get_request_params()` - to guarantee the records are returned in `ASC` order.
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

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        The override to add additional param to the api request to guarantee the `ASC` records order.

        Background:
            There is no possability to pass multiple request params from the YAML for the incremental streams,
            in addition to the `start_time_option` or similar, having them ignored those additional params,
            when we have `next_page_token`, which must be the single param to be passed to satisfy the API requirements.
        """

        params = super().get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        params["sort_by"] = "updated_at-asc"
        return params
