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
from airbyte_cdk.models import AirbyteMessage, AirbyteStream, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.models import Type as MessageType

# list of all possible HTTP methods which can be used for sending of request bodies
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, ResourceSchemaLoader
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from deprecated.classic import deprecated

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source
    from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type
StreamData = Union[Mapping[str, Any], AirbyteMessage]

JsonSchema = Mapping[str, Any]

# Streams that only support full refresh don't have a suitable cursor so this sentinel
# value is used to indicate that stream should not load the incoming state value
FULL_REFRESH_SENTINEL_STATE_KEY = "__ab_full_refresh_state_message"


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


class Stream(ABC):
    """
    Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.
    """

    # Use self.logger in subclasses to log any messages
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.streams.{self.name}")

    # TypeTransformer object to perform output data transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.NoTransform)

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return casing.camel_to_snake(self.__class__.__name__)

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        return None

    def read(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager,
        internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        sync_mode = configured_stream.sync_mode
        cursor_field = configured_stream.cursor_field

        slices = self.stream_slices(
            cursor_field=cursor_field,
            sync_mode=sync_mode,  # todo: change this interface to no longer rely on sync_mode for behavior
            stream_state=stream_state,
        )
        logger.debug(f"Processing stream slices for {self.name} (sync_mode: {sync_mode.name})", extra={"stream_slices": slices})

        has_slices = False
        record_counter = 0
        for _slice in slices:
            has_slices = True
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(_slice)
            records = self.read_records(
                sync_mode=sync_mode,  # todo: change this interface to no longer rely on sync_mode for behavior
                stream_slice=_slice,
                stream_state=stream_state,
                cursor_field=cursor_field or None,
            )
            for record_data_or_message in records:
                yield record_data_or_message
                if isinstance(record_data_or_message, Mapping) or (
                    hasattr(record_data_or_message, "type") and record_data_or_message.type == MessageType.RECORD
                ):
                    record_data = record_data_or_message if isinstance(record_data_or_message, Mapping) else record_data_or_message.record
                    stream_state = self.get_updated_state(stream_state, record_data)
                    record_counter += 1

                    if sync_mode == SyncMode.incremental:
                        # Checkpoint intervals are a bit controversial, but see below comment about why we're gating it right now
                        checkpoint_interval = self.state_checkpoint_interval
                        if checkpoint_interval and record_counter % checkpoint_interval == 0:
                            airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
                            yield airbyte_state_message

                    if internal_config.is_limit_reached(record_counter):
                        break

            if sync_mode == SyncMode.incremental:
                # Even though right now, only incremental streams running as incremental mode will emit periodic checkpoints. Rather than
                # overhaul how refresh interacts with the platform, this positions the code so that once we want to start emitting
                # periodic checkpoints in full refresh mode it can be done here
                airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
                yield airbyte_state_message

        if not has_slices or sync_mode == SyncMode.full_refresh:
            if sync_mode == SyncMode.full_refresh:
                # We use a dummy state if there is no suitable value provided by full_refresh streams that do not have a valid cursor.
                # Incremental streams running full_refresh mode emit a meaningful state
                stream_state = stream_state or {FULL_REFRESH_SENTINEL_STATE_KEY: True}

            # We should always emit a final state message for full refresh sync or streams that do not have any slices
            airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
            yield airbyte_state_message

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
    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        return len(self._wrapped_cursor_field()) > 0

    def _wrapped_cursor_field(self) -> List[str]:
        return [self.cursor_field] if isinstance(self.cursor_field, str) else self.cursor_field

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return []

    @property
    def namespace(self) -> Optional[str]:
        """
        Override to return the namespace of this stream, e.g. the Postgres schema which this stream will emit records for.
        :return: A string containing the name of the namespace.
        """
        return None

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

    @property
    @abstractmethod
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """

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

    def log_stream_sync_configuration(self) -> None:
        """
        Logs the configuration of this stream.
        """
        self.logger.debug(
            f"Syncing stream instance: {self.name}",
            extra={
                "primary_key": self.primary_key,
                "cursor_field": self.cursor_field,
            },
        )

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

    def _checkpoint_state(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
        self,
        stream_state: Mapping[str, Any],
        state_manager,
    ) -> AirbyteMessage:
        # First attempt to retrieve the current state using the stream's state property. We receive an AttributeError if the state
        # property is not implemented by the stream instance and as a fallback, use the stream_state retrieved from the stream
        # instance's deprecated get_updated_state() method.
        try:
            state_manager.update_state_for_stream(
                self.name, self.namespace, self.state  # type: ignore # we know the field might not exist...
            )

        except AttributeError:
            state_manager.update_state_for_stream(self.name, self.namespace, stream_state)
        return state_manager.create_state_message(self.name, self.namespace)
