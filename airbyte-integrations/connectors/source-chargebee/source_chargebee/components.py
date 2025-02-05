#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental import DeclarativeCursor
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


class PriorStateHandler:
    """
    PriorStateHandler is a class responsible for managing the state of a stream by tracking and updating the prior state values.

    Args:
        cursor_field (str): The field used to track the cursor position in the stream.
        stream_state (Optional[StreamState]): The current state of the stream.
        value_type (Optional[Any]): The default value type for the state.
        key (str): The key used to store the prior state in the stream state.

    Methods:
        Private:
            property: _exists: Checks if the prior state key exists in the stream state.
            propetry: _prior_state_value: Retrieves the prior state value for a specific stream.
            property: _stream_state_value: Retrieves the state value of the stream.
            func: _update(): Updates the stream state if the current stream state value is greater than the prior state value.
            func: _init(): Sets the initial state for the stream by copying the current state.

        Public:
            func: set(): Sets the state of the component. If the component does not exist, it initializes it. Otherwise, it updates the existing component.
    """

    def __init__(
        self,
        cursor_field: str,
        stream_state: Optional[StreamState] = None,
        value_type: Optional[Any] = None,
        key: Optional[str] = None,
    ) -> None:
        self._cursor_field = cursor_field
        self._stream_state = stream_state if stream_state is not None else {}
        self._default_value: Any = value_type() if value_type is not None else str()
        self._state_key: str = key if key else "prior_state"

    @property
    def _exists(self) -> bool:
        """
        Check if the prior state key exists in the stream state.

        Returns:
            bool: True if the state key exists in the stream state, False otherwise.
        """

        return self._state_key in self._stream_state

    @property
    def _prior_state_value(self) -> Any:
        """
        Property that retrieves the prior state value for a specific stream.

        Returns:
            int: The prior state value for the stream, or the default value type if not found.
        """

        return self._stream_state.get(self._state_key, {}).get(self._cursor_field, self._default_value)

    @property
    def _stream_state_value(self) -> Any:
        """
        Property that retrieves the state value of the stream.

        This method accesses the `stream_state` dictionary and returns the value
        associated with the `cursor_field` key. If the key is not found, it returns
        the default value specified by `self._default_value`.

        Returns:
            int: The state value of the stream.
        """

        return self._stream_state.get(self._cursor_field, self._default_value)

    def _update(self) -> None:
        """
        Updates the stream state if the current stream state value is greater than the prior state value.

        This method compares the current stream state value with the prior state value.
        If the current stream state value is greater, it updates the stream state with the new value
        using the state key and cursor field.
        """

        if self._stream_state_value > self._prior_state_value:
            self._stream_state[self._state_key] = {self._cursor_field: self._stream_state_value}

    def _init(self) -> None:
        """
        Sets the initial state for the stream by copying the current state.

        This method initializes the stream state by creating a copy of the current state
        and assigning it to the state key specific to this stream.
        """

        self._stream_state[self._state_key] = self._stream_state.copy()

    def set(self) -> None:
        """
        Sets the state of the component. If the component does not exist, it initializes it.
        Otherwise, it updates the existing component.
        """

        self._init() if not self._exists else self._update()


@dataclass
class IncrementalSingleSliceCursor(DeclarativeCursor):
    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._state = {}
        self._cursor = None
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        self._prior_state = PriorStateHandler(
            cursor_field=self.cursor_field.eval(self.config),
            stream_state=self._state,
            value_type=int,
        )

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
        return {**self._state}

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        return self.get_stream_state()

    def set_initial_state(self, stream_state: StreamState):
        """
        Sets the initial state of the stream based on the provided stream state.

        This method evaluates the cursor field using the configuration, retrieves the cursor value from the
        provided stream state, and updates the internal state and cursor if the cursor value is present.
        Additionally, it sets or updates the existing prior state with the cursor value.

        Args:
            stream_state (StreamState): The state of the stream to initialize from.
        """

        cursor_field = self.cursor_field.eval(self.config)
        cursor_value = stream_state.get(cursor_field)
        if cursor_value:
            self._state[cursor_field] = cursor_value
            self._cursor = cursor_value
            self._prior_state.set()

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
