#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class CustomFieldTransformation(RecordTransformation):
    """
    Add custom field based on condition. Jinja interpolation does not support list comprehension.
    https://github.com/airbytehq/airbyte/issues/23134
    """

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        Method to detect custom fields that start with 'cf_' from chargbee models.
        Args:
            record:
            {
                ...
                'cf_custom_fields': 'some_value',
                ...
            }

        Returns:
            record:
            {
                ...
                'custom_fields': [{
                    'name': 'cf_custom_fields',
                    'value': some_value'
                }],
                ...
            }
        """
        record["custom_fields"] = [{"name": k, "value": record.pop(k)} for k in record.copy() if k.startswith("cf_")]
        return record


@dataclass
class IncrementalSingleSliceCursor(Cursor):

    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._state = {}
        self._cursor = None
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update request params.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update request headers.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update body data.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Current implementation does not provide any options to update body json.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        return {}

    def get_stream_state(self) -> StreamState:
        return self._state

    def set_initial_state(self, stream_state: StreamState):
        cursor_field = self.cursor_field.eval(self.config)
        cursor_value = stream_state.get(cursor_field)
        if cursor_value:
            self._state[cursor_field] = cursor_value
            self._state["prior_state"] = self._state.copy()
            self._cursor = cursor_value

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Register a record with the cursor; the cursor instance can then use it to manage the state of the in-progress stream read.

        :param stream_slice: The current slice, which may or may not contain the most recently observed record
        :param record: the most recently-read record, which the cursor can use to update the stream state. Outwardly-visible changes to the
          stream state may need to be deferred depending on whether the source reliably orders records by the cursor field.
        """
        record_cursor_value = record.get(self.cursor_field.eval(self.config))
        if not record_cursor_value:
            return

        if self.is_greater_than_or_equal(record, self._state):
            self._cursor = record_cursor_value

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        cursor_field = self.cursor_field.eval(self.config)
        self._state[cursor_field] = self._cursor

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        yield StreamSlice(partition={}, cursor_slice={})

    def should_be_synced(self, record: Record) -> bool:
        """
        Evaluating if a record should be synced allows for filtering and stop condition on pagination
        """
        record_cursor_value = record.get(self.cursor_field.eval(self.config))
        return bool(record_cursor_value)

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
        cursor_field = self.cursor_field.eval(self.config)
        first_cursor_value = first.get(cursor_field) if first else None
        second_cursor_value = second.get(cursor_field) if second else None
        if first_cursor_value and second_cursor_value:
            return first_cursor_value > second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False
