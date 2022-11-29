#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from unittest.mock import call

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Level,
    Status,
    StreamDescriptor,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.checks.connection_checker import (
    AvailabilityStrategy,
    HTTPAvailabilityStrategy,
    ScopedAvailabilityStrategy,
)
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

logger = logging.getLogger("airbyte")


class MockSource(AbstractSource):
    def __init__(
        self,
        streams: List[Stream] = None,
    ):
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, ""

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self._streams:
            raise Exception("Stream is not set")
        return self._streams


class MockAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream) -> Tuple[bool, any]:
        if stream.name == "available_stream":
            return True, None
        return False, f"Could not reach stream '{stream.name}'."


class MockSourceWithAvailabilityStrategy(MockSource):
    @property
    def availability_strategy(self):
        return MockAvailabilityStrategy()


class MockScopedAvailabilityStrategy(ScopedAvailabilityStrategy):
    def get_granted_scopes(self) -> List[str]:
        return ["repo"]

    def required_scopes(self) -> Dict[str, List[str]]:
        return {"repos": ["repo"], "projectV2": ["read:project"]}


class MockSourceWithScopedAvailabilityStrategy(MockSource):
    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return MockScopedAvailabilityStrategy()


class MockSourceWithHTTPAvailabilityStrategy(MockSource):
    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return HTTPAvailabilityStrategy()


def test_availability_strategy():
    stream_1 = AirbyteStream(name="available_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    stream_2 = AirbyteStream(name="unavailable_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    source = MockSourceWithAvailabilityStrategy(streams=[stream_1, stream_2])
    assert isinstance(source.availability_strategy, MockAvailabilityStrategy)
    assert source.availability_strategy.check_availability(stream_1)[0] == True
    assert source.availability_strategy.check_availability(stream_2)[0] == False
    assert "Could not reach stream 'unavailable_stream'" in source.availability_strategy.check_availability(stream_2)[1]

def test_scoped_availability_strategy():
    stream_1 = AirbyteStream(name="repos", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    stream_2 = AirbyteStream(name="projectV2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    source = MockSourceWithScopedAvailabilityStrategy(streams=[stream_1, stream_2])
    assert source.availability_strategy.check_availability(stream_1)[0] == True
    assert source.availability_strategy.check_availability(stream_2)[0] == False
    assert "Missing required scopes: ['read:project']" in source.availability_strategy.check_availability(stream_2)[1]

def test_http_availability_strategy():
    stream_1 = AirbyteStream(name="available_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    stream_2 = AirbyteStream(name="unavailable_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
