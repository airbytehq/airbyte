
import logging
import typing
from abc import ABC
from typing import Iterable

from airbyte_cdk.sources.streams import Stream, FULL_REFRESH_SENTINEL_STATE_KEY
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig

from source_facebook_marketing.streams.concurrent_stream_reader import ConcurrentStreamReader


class AsyncStream(Stream, ABC):

    def __init__(self, max_workers: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_workers = max_workers

    def read(  # type: ignore  # ignoring typing for ConnectorStateManager because of circular dependencies
            self,
            configured_stream: ConfiguredAirbyteStream,
            logger: logging.Logger,
            slice_logger: SliceLogger,
            stream_state: typing.MutableMapping[str, typing.Any],
            state_manager,
            internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        with ConcurrentStreamReader(self, self.max_workers, logger, slice_logger, stream_state, state_manager, configured_stream) as reader:
            yield from reader

            if not reader.has_slices or configured_stream.sync_mode == SyncMode.full_refresh:
                if configured_stream.sync_mode == SyncMode.full_refresh:
                    # We use a dummy state if there is no suitable value provided by full_refresh streams that do not have a valid cursor.
                    # Incremental streams running full_refresh mode emit a meaningful state
                    stream_state = stream_state or {FULL_REFRESH_SENTINEL_STATE_KEY: True}

                # We should always emit a final state message for full refresh sync or streams that do not have any slices
                airbyte_state_message = self._checkpoint_state(stream_state, state_manager)
                yield airbyte_state_message
