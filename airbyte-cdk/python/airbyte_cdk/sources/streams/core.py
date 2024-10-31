#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import inspect
import itertools
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

import airbyte_cdk.sources.utils.casing as casing
from airbyte_cdk.models import AirbyteMessage, AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams.checkpoint import (
    CheckpointMode,
    CheckpointReader,
    Cursor,
    CursorBasedCheckpointReader,
    FullRefreshCheckpointReader,
    IncrementalCheckpointReader,
    LegacyCursorBasedCheckpointReader,
    ResumableFullRefreshCheckpointReader,
)
from airbyte_cdk.sources.types import StreamSlice

# list of all possible HTTP methods which can be used for sending of request bodies
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, ResourceSchemaLoader
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger, SliceLogger
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from deprecated import deprecated

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type
StreamData = Union[Mapping[str, Any], AirbyteMessage]

JsonSchema = Mapping[str, Any]

NO_CURSOR_STATE_KEY = "__ab_no_cursor_state_message"


def package_name_from_class(cls: object) -> str:
    """Find the package name given a class name"""
    module = inspect.getmodule(cls)
    if module is not None:
        return module.__name__.split(".")[0]
    else:
        raise ValueError(f"Could not find package name for class {cls}")


class CheckpointMixin(ABC):
    """Mixin for a stream that implements reading and writing the internal state used to checkpoint sync progress to the platform

    class CheckpointedStream(Stream, CheckpointMixin):
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


@deprecated(version="0.87.0", reason="Deprecated in favor of the CheckpointMixin which offers similar functionality")
class IncrementalMixin(CheckpointMixin, ABC):
    """Mixin to make stream incremental.

    class IncrementalStream(Stream, IncrementalMixin):
        @property
        def state(self):
            return self._state

        @state.setter
        def state(self, value):
            self._state[self.cursor_field] = value[self.cursor_field]
    """


@dataclass
class StreamClassification:
    is_legacy_format: bool
    has_multiple_slices: bool


# Moved to class declaration since get_updated_state is called on every record for incremental syncs, and thus the @deprecated decorator as well.
@deprecated(
    version="0.1.49",
    reason="Deprecated method get_updated_state, You should use explicit state property instead, see IncrementalMixin docs.",
    action="ignore",
)
class Stream(ABC):
    """
    Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.
    """

    _configured_json_schema: Optional[Dict[str, Any]] = None
    _exit_on_rate_limit: bool = False

    # Use self.logger in subclasses to log any messages
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.streams.{self.name}")

    # TypeTransformer object to perform output data transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.NoTransform)

    cursor: Optional[Cursor] = None

    has_multiple_slices = False

    @cached_property
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
        self.configured_json_schema = configured_stream.stream.json_schema

        # WARNING: When performing a read() that uses incoming stream state, we MUST use the self.state that is defined as
        # opposed to the incoming stream_state value. Because some connectors like ones using the file-based CDK modify
        # state before setting the value on the Stream attribute, the most up-to-date state is derived from Stream.state
        # instead of the stream_state parameter. This does not apply to legacy connectors using get_updated_state().
        try:
            stream_state = self.state  # type: ignore # we know the field might not exist...
        except AttributeError:
            pass

        should_checkpoint = bool(state_manager)
        checkpoint_reader = self._get_checkpoint_reader(
            logger=logger, cursor_field=cursor_field, sync_mode=sync_mode, stream_state=stream_state
        )

        next_slice = checkpoint_reader.next()
        record_counter = 0
        stream_state_tracker = copy.deepcopy(stream_state)
        while next_slice is not None:
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(next_slice)
            records = self.read_records(
                sync_mode=sync_mode,  # todo: change this interface to no longer rely on sync_mode for behavior
                stream_slice=next_slice,
                stream_state=stream_state,
                cursor_field=cursor_field or None,
            )
            for record_data_or_message in records:
                yield record_data_or_message
                if isinstance(record_data_or_message, Mapping) or (
                    hasattr(record_data_or_message, "type") and record_data_or_message.type == MessageType.RECORD
                ):
                    record_data = record_data_or_message if isinstance(record_data_or_message, Mapping) else record_data_or_message.record

                    # Thanks I hate it. RFR fundamentally doesn't fit with the concept of the legacy Stream.get_updated_state()
                    # method because RFR streams rely on pagination as a cursor. Stream.get_updated_state() was designed to make
                    # the CDK manage state using specifically the last seen record. don't @ brian.lai
                    #
                    # Also, because the legacy incremental state case decouples observing incoming records from emitting state, it
                    # requires that we separate CheckpointReader.observe() and CheckpointReader.get_checkpoint() which could
                    # otherwise be combined.
                    if self.cursor_field:
                        # Some connectors have streams that implement get_updated_state(), but do not define a cursor_field. This
                        # should be fixed on the stream implementation, but we should also protect against this in the CDK as well
                        stream_state_tracker = self.get_updated_state(stream_state_tracker, record_data)
                        self._observe_state(checkpoint_reader, stream_state_tracker)
                    record_counter += 1

                    checkpoint_interval = self.state_checkpoint_interval
                    checkpoint = checkpoint_reader.get_checkpoint()
                    if should_checkpoint and checkpoint_interval and record_counter % checkpoint_interval == 0 and checkpoint is not None:
                        airbyte_state_message = self._checkpoint_state(checkpoint, state_manager=state_manager)
                        yield airbyte_state_message

                    if internal_config.is_limit_reached(record_counter):
                        break
            self._observe_state(checkpoint_reader)
            checkpoint_state = checkpoint_reader.get_checkpoint()
            if should_checkpoint and checkpoint_state is not None:
                airbyte_state_message = self._checkpoint_state(checkpoint_state, state_manager=state_manager)
                yield airbyte_state_message

            next_slice = checkpoint_reader.next()

        checkpoint = checkpoint_reader.get_checkpoint()
        if should_checkpoint and checkpoint is not None:
            airbyte_state_message = self._checkpoint_state(checkpoint, state_manager=state_manager)
            yield airbyte_state_message

    def read_only_records(self, state: Optional[Mapping[str, Any]] = None) -> Iterable[StreamData]:
        """
        Helper method that performs a read on a stream with an optional state and emits records. If the parent stream supports
        incremental, this operation does not update the stream's internal state (if it uses the modern state setter/getter)
        or emit state messages.
        """

        configured_stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name=self.name,
                json_schema={},
                supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            ),
            sync_mode=SyncMode.incremental if state else SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
        )

        yield from self.read(
            configured_stream=configured_stream,
            logger=self.logger,
            slice_logger=DebugSliceLogger(),
            stream_state=dict(state) if state else {},  # read() expects MutableMapping instead of Mapping which is used more often
            state_manager=None,
            internal_config=InternalConfig(),
        )

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
        stream = AirbyteStream(
            name=self.name,
            json_schema=dict(self.get_json_schema()),
            supported_sync_modes=[SyncMode.full_refresh],
            is_resumable=self.is_resumable,
        )

        if self.namespace:
            stream.namespace = self.namespace

        # If we can offer incremental we always should. RFR is always less reliable than incremental which uses a real cursor value
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

    @property
    def is_resumable(self) -> bool:
        """
        :return: True if this stream allows the checkpointing of sync progress and can resume from it on subsequent attempts.
        This differs from supports_incremental because certain kinds of streams like those supporting resumable full refresh
        can checkpoint progress in between attempts for improved fault tolerance. However, they will start from the beginning
        on the next sync job.
        """
        if self.supports_incremental:
            return True
        if self.has_multiple_slices:
            # We temporarily gate substream to not support RFR because puts a pretty high burden on connector developers
            # to structure stream state in a very specific way. We also can't check for issubclass(HttpSubStream) because
            # not all substreams implement the interface and it would be a circular dependency so we use parent as a surrogate
            return False
        elif hasattr(type(self), "state") and getattr(type(self), "state").fset is not None:
            # Modern case where a stream manages state using getter/setter
            return True
        else:
            # Legacy case where the CDK manages state via the get_updated_state() method. This is determined by checking if
            # the stream's get_updated_state() differs from the Stream class and therefore has been overridden
            return type(self).get_updated_state != Stream.get_updated_state

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

    @property
    def exit_on_rate_limit(self) -> bool:
        """Exit on rate limit getter, should return bool value. False if the stream will retry endlessly when rate limited."""
        return self._exit_on_rate_limit

    @exit_on_rate_limit.setter
    def exit_on_rate_limit(self, value: bool) -> None:
        """Exit on rate limit setter, accept bool value."""
        self._exit_on_rate_limit = value

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
        yield StreamSlice(partition={}, cursor_slice={})

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

    def get_cursor(self) -> Optional[Cursor]:
        """
        A Cursor is an interface that a stream can implement to manage how its internal state is read and updated while
        reading records. Historically, Python connectors had no concept of a cursor to manage state. Python streams need
        to define a cursor implementation and override this method to manage state through a Cursor.
        """
        return self.cursor

    def _get_checkpoint_reader(
        self,
        logger: logging.Logger,
        cursor_field: Optional[List[str]],
        sync_mode: SyncMode,
        stream_state: MutableMapping[str, Any],
    ) -> CheckpointReader:
        mappings_or_slices = self.stream_slices(
            cursor_field=cursor_field,
            sync_mode=sync_mode,  # todo: change this interface to no longer rely on sync_mode for behavior
            stream_state=stream_state,
        )

        # Because of poor foresight, we wrote the default Stream.stream_slices() method to return [None] which is confusing and
        # has now normalized this behavior for connector developers. Now some connectors return [None]. This is objectively
        # misleading and a more ideal interface is [{}] to indicate we still want to iterate over one slice, but with no
        # specific slice values. None is bad, and now I feel bad that I have to write this hack.
        if mappings_or_slices == [None]:
            mappings_or_slices = [{}]

        slices_iterable_copy, iterable_for_detecting_format = itertools.tee(mappings_or_slices, 2)
        stream_classification = self._classify_stream(mappings_or_slices=iterable_for_detecting_format)

        # Streams that override has_multiple_slices are explicitly indicating that they will iterate over
        # multiple partitions. Inspecting slices to automatically apply the correct cursor is only needed as
        # a backup. So if this value was already assigned to True by the stream, we don't need to reassign it
        self.has_multiple_slices = self.has_multiple_slices or stream_classification.has_multiple_slices

        cursor = self.get_cursor()
        if cursor:
            cursor.set_initial_state(stream_state=stream_state)

        checkpoint_mode = self._checkpoint_mode

        if cursor and stream_classification.is_legacy_format:
            return LegacyCursorBasedCheckpointReader(stream_slices=slices_iterable_copy, cursor=cursor, read_state_from_cursor=True)
        elif cursor:
            return CursorBasedCheckpointReader(
                stream_slices=slices_iterable_copy,
                cursor=cursor,
                read_state_from_cursor=checkpoint_mode == CheckpointMode.RESUMABLE_FULL_REFRESH,
            )
        elif checkpoint_mode == CheckpointMode.RESUMABLE_FULL_REFRESH:
            # Resumable full refresh readers rely on the stream state dynamically being updated during pagination and does
            # not iterate over a static set of slices.
            return ResumableFullRefreshCheckpointReader(stream_state=stream_state)
        elif checkpoint_mode == CheckpointMode.INCREMENTAL:
            return IncrementalCheckpointReader(stream_slices=slices_iterable_copy, stream_state=stream_state)
        else:
            return FullRefreshCheckpointReader(stream_slices=slices_iterable_copy)

    @property
    def _checkpoint_mode(self) -> CheckpointMode:
        if self.is_resumable and len(self._wrapped_cursor_field()) > 0:
            return CheckpointMode.INCREMENTAL
        elif self.is_resumable:
            return CheckpointMode.RESUMABLE_FULL_REFRESH
        else:
            return CheckpointMode.FULL_REFRESH

    @staticmethod
    def _classify_stream(mappings_or_slices: Iterator[Optional[Union[Mapping[str, Any], StreamSlice]]]) -> StreamClassification:
        """
        This is a bit of a crazy solution, but also the only way we can detect certain attributes about the stream since Python
        streams do not follow consistent implementation patterns. We care about the following two attributes:
        - is_substream: Helps to incrementally release changes since substreams w/ parents are much more complicated. Also
          helps de-risk the release of changes that might impact all connectors
        - uses_legacy_slice_format: Since the checkpoint reader must manage a complex state object, we opted to have it always
          use the structured StreamSlice object. However, this requires backwards compatibility with Python sources that only
          support the legacy mapping object

        Both attributes can eventually be deprecated once stream's define this method deleted once substreams have been implemented and
        legacy connectors all adhere to the StreamSlice object.
        """
        if not mappings_or_slices:
            raise ValueError("A stream should always have at least one slice")
        try:
            next_slice = next(mappings_or_slices)
            if isinstance(next_slice, StreamSlice) and next_slice == StreamSlice(partition={}, cursor_slice={}):
                is_legacy_format = False
                slice_has_value = False
            elif next_slice == {}:
                is_legacy_format = True
                slice_has_value = False
            elif isinstance(next_slice, StreamSlice):
                is_legacy_format = False
                slice_has_value = True
            else:
                is_legacy_format = True
                slice_has_value = True
        except StopIteration:
            # If the stream has no slices, the format ultimately does not matter since no data will get synced. This is technically
            # a valid case because it is up to the stream to define its slicing behavior
            return StreamClassification(is_legacy_format=False, has_multiple_slices=False)

        if slice_has_value:
            # If the first slice contained a partition value from the result of stream_slices(), this is a substream that might
            # have multiple parent records to iterate over
            return StreamClassification(is_legacy_format=is_legacy_format, has_multiple_slices=slice_has_value)

        try:
            # If stream_slices() returns multiple slices, this is also a substream that can potentially generate empty slices
            next(mappings_or_slices)
            return StreamClassification(is_legacy_format=is_legacy_format, has_multiple_slices=True)
        except StopIteration:
            # If the result of stream_slices() only returns a single empty stream slice, then we know this is a regular stream
            return StreamClassification(is_legacy_format=is_legacy_format, has_multiple_slices=False)

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

    def _observe_state(self, checkpoint_reader: CheckpointReader, stream_state: Optional[Mapping[str, Any]] = None) -> None:
        """
        Convenience method that attempts to read the Stream's state using the recommended way of connector's managing their
        own state via state setter/getter. But if we get back an AttributeError, then the legacy Stream.get_updated_state()
        method is used as a fallback method.
        """

        # This is an inversion of the original logic that used to try state getter/setters first. As part of the work to
        # automatically apply resumable full refresh to all streams, all HttpStream classes implement default state
        # getter/setter methods, we should default to only using the incoming stream_state parameter value is {} which
        # indicates the stream does not override the default get_updated_state() implementation. When the default method
        # is not overridden, then the stream defers to self.state getter
        if stream_state:
            checkpoint_reader.observe(stream_state)
        elif type(self).get_updated_state == Stream.get_updated_state:
            # We only default to the state getter/setter if the stream does not use the legacy get_updated_state() method
            try:
                new_state = self.state  # type: ignore # This will always exist on HttpStreams, but may not for Stream
                if new_state:
                    checkpoint_reader.observe(new_state)
            except AttributeError:
                pass

    def _checkpoint_state(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
        self,
        stream_state: Mapping[str, Any],
        state_manager,
    ) -> AirbyteMessage:
        # todo: This can be consolidated into one ConnectorStateManager.update_and_create_state_message() method, but I want
        #  to reduce changes right now and this would span concurrent as well
        state_manager.update_state_for_stream(self.name, self.namespace, stream_state)
        return state_manager.create_state_message(self.name, self.namespace)

    @property
    def configured_json_schema(self) -> Optional[Dict[str, Any]]:
        """
        This property is set from the read method.

        :return Optional[Dict]: JSON schema from configured catalog if provided, otherwise None.
        """
        return self._configured_json_schema

    @configured_json_schema.setter
    def configured_json_schema(self, json_schema: Dict[str, Any]) -> None:
        self._configured_json_schema = self._filter_schema_invalid_properties(json_schema)

    def _filter_schema_invalid_properties(self, configured_catalog_json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters the properties in json_schema that are not present in the stream schema.
        Configured Schemas can have very old fields, so we need to housekeeping ourselves.
        """
        configured_schema: Any = configured_catalog_json_schema.get("properties", {})
        stream_schema_properties: Any = self.get_json_schema().get("properties", {})

        configured_keys = configured_schema.keys()
        stream_keys = stream_schema_properties.keys()
        invalid_properties = configured_keys - stream_keys
        if not invalid_properties:
            return configured_catalog_json_schema

        self.logger.warning(
            f"Stream {self.name}: the following fields are deprecated and cannot be synced. {invalid_properties}. Refresh the connection's source schema to resolve this warning."
        )

        valid_configured_schema_properties_keys = stream_keys & configured_keys
        valid_configured_schema_properties = {}

        for configured_schema_property in valid_configured_schema_properties_keys:
            valid_configured_schema_properties[configured_schema_property] = stream_schema_properties[configured_schema_property]

        return {**configured_catalog_json_schema, "properties": valid_configured_schema_properties}
