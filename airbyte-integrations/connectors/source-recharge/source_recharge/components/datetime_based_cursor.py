#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class RechargeDateTimeBasedCursor(DatetimeBasedCursor):
    """
    Override for the default `DatetimeBasedCursor` to make self.close_slice() to produce `min` value instead of `max` value.

    1) Override for the `close_slice()` - to make the SOURCE STATE proccessed correctly:
        emit_state_from: str - `most_recent_record` or `stream_slice`, determines what value to emit when it comes to the STATE value.

           @: `most_recent_record` == the actual value from the RECORD
           @: `stream_slice` == the upper boundary value of the SLICER's `stream_slice_end_value`, where the sync must be STOPPED.

    2) Override for the `get_request_params()` - to guarantee the records are returned in `ASC` order.
    """

    emit_state_from: Union[InterpolatedString, str] = "stream_slice"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._state_selector_keys: List[str] = ["most_recent_record", "stream_slice"]
        self._emit_state_from = InterpolatedString.create(self.emit_state_from, parameters=parameters).eval(self.config)
        if self._emit_state_from not in self._state_selector_keys:
            raise ValueError(
                f"The `emit_state_from` is not one of: {self._state_selector_keys}, actual value is: `{self._emit_state_from}`."
            )
        super().__post_init__(parameters=parameters)

    def has_emit_state_from_key_in_record(self, cursor_values: Mapping[str, Any]) -> bool:
        """
        Determine whether or not we have the target key in the `cursor_values`
        """
        return self._emit_state_from in cursor_values.keys()

    def get_state_to_stream_slice(self, cursor_values: Mapping[str, Any]) -> Optional[datetime]:
        """
        Get the `stream_slice` cursor value from `cursor_values`
        """
        return cursor_values.get("stream_slice")

    def get_state_to_emit_state_from(self, cursor_values: Mapping[str, Any]) -> Optional[datetime]:
        """
        Determine whether or not we have the target key in the `cursor_values`
        """
        return cursor_values.get(self._emit_state_from)

    def make_cursor_values(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> Mapping[str, Optional[datetime]]:
        """
        Makes the `cursor_values` using `stream_slice` and `most_recent_record`.
        """
        last_record_cursor_value = most_recent_record.get(self._cursor_field.eval(self.config)) if most_recent_record else None
        stream_slice_value_end = stream_slice.get(self._partition_field_end.eval(self.config))
        cursor_values: dict = {
            "most_recent_record": self.parse_date(last_record_cursor_value) if last_record_cursor_value else None,
            "stream_slice": self.parse_date(stream_slice_value_end) if stream_slice_value_end else None,
        }
        # filter out the `NONE` STATE values from the `cursor_values`
        return {key: value for key, value in cursor_values.items() if value is not None}

    def process_state(self, cursor_values: Mapping[str, Any]) -> None:
        """
        Allow to get the specific STATE value which is relevant for the Source Logic.
        Default is: `stream_slice` as of the default Low-Code `DatetimeBasedCursor` logic.

        Possible values are:
            - cursor
            - most_recent_record
            - stream_slice
        """
        if not self.has_emit_state_from_key_in_record(cursor_values):
            # fallback to the default STATE value logic,
            # if the `most_recent_record` is None or missing,
            # because the `stream_slice_end_value` always exists.
            return self.get_state_to_stream_slice(cursor_values)
        else:
            # set the STATE value to the `most_recent_record` value
            return self.get_state_to_emit_state_from(cursor_values)

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        """
        Override for the default CDK `close_slice()` method,
        to provide the ability to select between the available `cursor_values`.
        """
        self._cursor = self.process_state(self.make_cursor_values(stream_slice, most_recent_record))

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
