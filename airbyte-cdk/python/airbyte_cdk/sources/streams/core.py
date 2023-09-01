#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import inspect
import logging
import typing
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import airbyte_cdk.sources.utils.casing as casing
from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream

# list of all possible HTTP methods which can be used for sending of request bodies
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, ResourceSchemaLoader
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.types import StreamData
from deprecated.classic import deprecated

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source
    from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type

JsonSchema = Mapping[str, Any]
StreamData = StreamData


def package_name_from_class(cls: object) -> str:
    """Find the package name given a class name"""
    module = inspect.getmodule(cls)
    if module is not None:
        return module.__name__.split(".")[0]
    else:
        raise ValueError(f"Could not find package name for class {cls}")


class IncrementalMixin(ABC):
    """Mixin to make stream incremental.

    class IncrementalStream(Stream, IncrementalMixin):
        @property
        def state(self):
            return self._state

        @state.setter
        def state(self, value):
            self._state[self.cursor_field] = value[self.cursor_field]
    """

    @property
    @abstractmethod
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a cursor_value:
            {
                self.cursor_field: "cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

    @state.setter
    @abstractmethod
    def state(self, value: MutableMapping[str, Any]) -> None:
        """State setter, accept state serialized by state getter."""


class Stream(AbstractStream, ABC):
    """
    Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.
    """

    def read(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
        internal_config: InternalConfig = InternalConfig(),
    ) -> Iterable[StreamData]:
        slices = self.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field)
        logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        for _slice in slices:
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(_slice)
            record_data_or_messages = self.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
            )
            for record_data_or_message in record_data_or_messages:
                yield record_data_or_message
                if AbstractStream.is_record(record_data_or_message):
                    total_records_counter += 1
                    if internal_config and internal_config.is_limit_reached(total_records_counter):
                        return

    # Use self.logger in subclasses to log any messages
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.streams.{self.name}")

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return casing.camel_to_snake(self.__class__.__name__)

    @abstractmethod
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """
        This method should be overridden by subclasses to read records based on the inputs
        """

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        # TODO show an example of using pydantic to define the JSON schema, or reading an OpenAPI spec
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(self.name)

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(name=self.name, json_schema=dict(self.get_json_schema()), supported_sync_modes=[SyncMode.full_refresh])

        if self.namespace:
            stream.namespace = self.namespace

        if self.supports_incremental:
            stream.source_defined_cursor = self.source_defined_cursor
            stream.supported_sync_modes.append(SyncMode.incremental)  # type: ignore
            stream.default_cursor_field = self._wrapped_cursor_field()

        keys = Stream._wrapped_primary_key(self.primary_key)
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = keys

        return stream

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return []

    @property
    def source_defined_cursor(self) -> bool:
        """
        Return False if the cursor can be configured by the user.
        """
        return True

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        """
        Checks whether this stream is available.

        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then this stream
          is available, and no str is required. Otherwise, this stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """
        if self.availability_strategy:
            return self.availability_strategy.check_availability(self, logger, source)
        return True, None

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        """
        :return: The AvailabilityStrategy used to check whether this stream is available.
        """
        return None

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        return [None]

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """
        Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.

        Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.

        return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.
        """
        return None

    @deprecated(version="0.1.49", reason="You should use explicit state property instead, see IncrementalMixin docs.")
    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """Override to extract state from the latest record. Needed to implement incremental sync.

        Inspects the latest record extracted from the data source and the current state object and return an updated state object.

        For example: if the state object is based on created_at timestamp, and the current state is {'created_at': 10}, and the latest_record is
        {'name': 'octavia', 'created_at': 20 } then this method would return {'created_at': 20} to indicate state should be updated to this object.

        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object
        """
        return {}

    @staticmethod
    def _wrapped_primary_key(keys: Optional[Union[str, List[str], List[List[str]]]]) -> Optional[List[List[str]]]:
        """
        :return: wrap the primary_key property in a list of list of strings required by the Airbyte Stream object.
        """
        if not keys:
            return None

        if isinstance(keys, str):
            return [[keys]]
        elif isinstance(keys, list):
            wrapped_keys = []
            for component in keys:
                if isinstance(component, str):
                    wrapped_keys.append([component])
                elif isinstance(component, list):
                    wrapped_keys.append(component)
                else:
                    raise ValueError(f"Element must be either list or str. Got: {type(component)}")
            return wrapped_keys
        else:
            raise ValueError(f"Element must be either list or str. Got: {type(keys)}")
