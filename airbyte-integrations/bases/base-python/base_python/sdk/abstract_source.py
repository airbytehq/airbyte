"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import copy
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
from airbyte_protocol import Type as MessageType
from base_python.integration import Source
from base_python.logger import AirbyteLogger
from base_python.sdk.streams.core import Stream


class AbstractSource(Source, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful and we can connect to the underlying data
        source using the provided configuration.
        Otherwise, the input config cannot be used to connect to the underlying data source, and the "error" object should describe what went wrong.
        The error object will be cast to string to display the problem to the user.
        """

    @abstractmethod
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :return: A list of the streams in this source connector
        """

    @property
    def name(self) -> str:
        """Source name"""
        return self.__class__.__name__

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Discover streams"""
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        return AirbyteCatalog(streams=streams)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Check connection"""
        check_succeeded, error = self.check_connection(logger, config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(error))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:

        state = state or {}
        total_state = copy.deepcopy(state)
        logger.info(f"Starting syncing {self.name}")
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        for configured_stream in catalog.streams:
            try:
                stream_instance = stream_instances[configured_stream.stream.name]
                yield from self._read_stream(
                    logger=logger, stream_instance=stream_instance, configured_stream=configured_stream, state=total_state
                )
            except Exception as e:
                logger.exception(f"Encountered an exception while reading stream {self.name}")
                raise e

        logger.info(f"Finished syncing {self.name}")

    def _read_stream(
        self, logger: AirbyteLogger, stream_instance: Stream, configured_stream: ConfiguredAirbyteStream, state: MutableMapping[str, Any]
    ) -> Iterator[AirbyteMessage]:
        stream_name = configured_stream.stream.name
        use_incremental = configured_stream.sync_mode == SyncMode.incremental and stream_instance.supports_incremental

        stream_state = {}
        if use_incremental and state.get(stream_name):
            logger.info(f"Set state of {stream_name} stream to {state.get(stream_name)}")
            stream_state = state.get(stream_name)

        logger.info(f"Syncing stream: {stream_name} ")
        record_counter = 0
        for record in stream_instance.read_stream(configured_stream=configured_stream, stream_state=copy.deepcopy(stream_state)):
            now_millis = int(datetime.now().timestamp()) * 1000
            message = AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=now_millis)
            yield AirbyteMessage(type=MessageType.RECORD, record=message)

            record_counter += 1
            if use_incremental:
                stream_state = stream_instance.get_updated_state(stream_state, record)
                if record_counter % stream_instance.state_checkpoint_interval == 0:
                    state[stream_name] = stream_state
                    yield AirbyteMessage(type=MessageType.STATE, state=AirbyteStateMessage(data=state))

        if use_incremental and stream_state:
            state[stream_name] = stream_state
            # output state object only together with other stream states
            yield AirbyteMessage(type=MessageType.STATE, state=AirbyteStateMessage(data=state))
