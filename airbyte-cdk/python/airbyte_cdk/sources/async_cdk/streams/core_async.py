#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams.core import Stream, StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger

if TYPE_CHECKING:
    from airbyte_cdk.sources.streams.http.availability_strategy_async import AsyncHttpAvailabilityStrategy


class AsyncStream(Stream, ABC):
    """
    Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.
    """

    async def read_full_refresh(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
    ) -> Iterable[StreamData]:
        async for _slice in self.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field):
            logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)", extra={"stream_slice": _slice})
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(_slice)
            async for record in self.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
            ):
                yield record

    async def read_incremental(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager,
        per_stream_state_enabled: bool,
        internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        slices = self.stream_slices(
            cursor_field=cursor_field,
            sync_mode=SyncMode.incremental,
            stream_state=stream_state,
        )
        logger.debug(f"Processing stream slices for {self.name} (sync_mode: incremental)", extra={"stream_slices": slices})

        has_slices = False
        record_counter = 0
        async for _slice in slices:
            has_slices = True
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(_slice)
            records = self.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=_slice,
                stream_state=stream_state,
                cursor_field=cursor_field or None,
            )
            async for record_data_or_message in records:
                yield record_data_or_message
                if isinstance(record_data_or_message, Mapping) or (
                    hasattr(record_data_or_message, "type") and record_data_or_message.type == MessageType.RECORD
                ):
                    record_data = record_data_or_message if isinstance(record_data_or_message, Mapping) else record_data_or_message.record
                    stream_state = self.get_updated_state(stream_state, record_data)
                    checkpoint_interval = self.state_checkpoint_interval
                    record_counter += 1
                    if checkpoint_interval and record_counter % checkpoint_interval == 0:
                        yield self._checkpoint_state(stream_state, state_manager, per_stream_state_enabled)

                    if internal_config.is_limit_reached(record_counter):
                        break

            yield self._checkpoint_state(stream_state, state_manager, per_stream_state_enabled)

        if not has_slices:
            # Safety net to ensure we always emit at least one state message even if there are no slices
            checkpoint = self._checkpoint_state(stream_state, state_manager, per_stream_state_enabled)
            yield checkpoint

    @abstractmethod
    async def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """
        This method should be overridden by subclasses to read records based on the inputs
        """

    async def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        yield None

    async def ensure_session(self, *args: Any, **kwargs: Any) -> Any:
        """
        Override to define a session object on the stream.
        """
        pass

    @property
    def availability_strategy(self) -> Optional["AsyncHttpAvailabilityStrategy"]:
        """
        :return: The AvailabilityStrategy used to check whether this stream is available.
        """
        return None

    async def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
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
            return await self.availability_strategy.check_availability(self, logger, source)
        return True, None

    async def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        return None
