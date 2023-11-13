#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import copy
import logging
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Type

from airbyte_cdk.models import (
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
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.source import Source

from .client import BaseClient


class BaseSource(Source):
    """Base source that designed to work with clients derived from BaseClient"""

    client_class: Type[BaseClient]

    @property
    def name(self) -> str:
        """Source name"""
        return self.__class__.__name__

    def _get_client(self, config: Mapping):
        """Construct client"""
        return self.client_class(**config)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Discover streams"""
        client = self._get_client(config)

        return AirbyteCatalog(streams=[stream for stream in client.streams])

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Check connection"""
        client = self._get_client(config)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(error))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
        self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Iterable[AirbyteMessage]:
        state = state or {}
        client = self._get_client(config)

        logger.info(f"Starting syncing {self.name}")
        total_state = copy.deepcopy(state)
        for configured_stream in catalog.streams:
            try:
                yield from self._read_stream(logger=logger, client=client, configured_stream=configured_stream, state=total_state)

            except Exception:
                logger.exception(f"Encountered an exception while reading stream {self.name}")
                raise

        logger.info(f"Finished syncing {self.name}")

    def _read_stream(
        self, logger: logging.Logger, client: BaseClient, configured_stream: ConfiguredAirbyteStream, state: MutableMapping[str, Any]
    ):
        stream_name = configured_stream.stream.name
        use_incremental = configured_stream.sync_mode == SyncMode.incremental and client.stream_has_state(stream_name)

        if use_incremental and state.get(stream_name):
            logger.info(f"Set state of {stream_name} stream to {state.get(stream_name)}")
            client.set_stream_state(stream_name, state.get(stream_name))

        logger.info(f"Syncing {stream_name} stream")
        for record in client.read_stream(configured_stream.stream):
            now = int(datetime.now().timestamp()) * 1000
            message = AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=now)
            yield AirbyteMessage(type=MessageType.RECORD, record=message)

        if use_incremental and client.get_stream_state(stream_name):
            state[stream_name] = client.get_stream_state(stream_name)
            # output state object only together with other stream states
            yield AirbyteMessage(type=MessageType.STATE, state=AirbyteStateMessage(data=state))
