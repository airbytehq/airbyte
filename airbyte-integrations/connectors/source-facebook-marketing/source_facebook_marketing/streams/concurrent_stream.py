
import logging
from abc import ABC
from typing import Iterable, Mapping, MutableMapping, Any

from airbyte_cdk.sources.streams import Stream, FULL_REFRESH_SENTINEL_STATE_KEY
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.models import Type as MessageType

from source_facebook_marketing.streams.concurrent_stream_reader import ConcurrentStreamReader


class ConcurrentStream(Stream, ABC):

    def __init__(self, max_workers: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_workers = max_workers

    def read(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
            self,
            configured_stream: ConfiguredAirbyteStream,
            logger: logging.Logger,
            slice_logger: SliceLogger,
            stream_state: MutableMapping[str, Any],
            state_manager,
            internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        has_slices = False
        record_counter = 0
        with ConcurrentStreamReader(self, self.max_workers, logger, slice_logger, stream_state, configured_stream) as reader:
            for record_data_or_message in reader:
                yield record_data_or_message
                if isinstance(record_data_or_message, Mapping) or (
                        hasattr(record_data_or_message, "type") and record_data_or_message.type == MessageType.RECORD
                ):
                    has_slices = True

                    record_data = record_data_or_message if isinstance(record_data_or_message, Mapping) else record_data_or_message.record
                    stream_state = self.get_updated_state(stream_state, record_data)
                    record_counter += 1

                if configured_stream.sync_mode == SyncMode.incremental:
                    checkpoint_interval = self.state_checkpoint_interval
                    if checkpoint_interval and record_counter % checkpoint_interval == 0:
                        airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
                        yield airbyte_state_message

                if internal_config.is_limit_reached(record_counter):
                    break

            if configured_stream.sync_mode == SyncMode.incremental:
                # Even though right now, only incremental streams running as incremental mode will emit periodic checkpoints. Rather than
                # overhaul how refresh interacts with the platform, this positions the code so that once we want to start emitting
                # periodic checkpoints in full refresh mode it can be done here
                airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
                yield airbyte_state_message

        if not has_slices or configured_stream.sync_mode == SyncMode.full_refresh:
            if configured_stream.sync_mode == SyncMode.full_refresh:
                # We use a dummy state if there is no suitable value provided by full_refresh streams that do not have a valid cursor.
                # Incremental streams running full_refresh mode emit a meaningful state
                stream_state = stream_state or {FULL_REFRESH_SENTINEL_STATE_KEY: True}

            # We should always emit a final state message for full refresh sync or streams that do not have any slices
            airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
            yield airbyte_state_message
