#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple, Union
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from pytest import fixture

logger = logging.getLogger("airbyte")


class _MockSource(ConcurrentSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        streams: List[Stream] = None,
        per_stream: bool = True,
        message_repository: MessageRepository = InMemoryMessageRepository(),
        threadpool: ThreadPoolManager = ThreadPoolManager(
            concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="workerpool"), logger
        ),
        exception_on_missing_stream: bool = True,
    ):
        super().__init__(threadpool, message_repository)
        self._streams = streams
        self.check_lambda = check_lambda
        self.per_stream = per_stream
        self.exception_on_missing_stream = exception_on_missing_stream
        self._message_repository = message_repository

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        if self.check_lambda:
            return self.check_lambda()
        return False, "Missing callable."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self._streams:
            raise Exception("Stream is not set")
        return [StreamFacade.create_from_stream(stream, self, logger, None, NoopCursor()) for stream in self._streams]

    @property
    def raise_exception_on_missing_stream(self) -> bool:
        return self.exception_on_missing_stream

    @property
    def per_stream_state_enabled(self) -> bool:
        return self.per_stream

    @property
    def message_repository(self):
        return self._message_repository


MESSAGE_FROM_REPOSITORY = Mock()


@fixture
def message_repository():
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = [message for message in [MESSAGE_FROM_REPOSITORY]]
    return message_repository


class _MockStream(Stream):
    def __init__(
        self,
        inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[Mapping[str, Any]]]] = None,
        name: str = None,
    ):
        self._inputs_and_mocked_outputs = inputs_and_mocked_outputs
        self._name = name

    @property
    def name(self):
        return self._name

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:  # type: ignore
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if self._inputs_and_mocked_outputs:
            for _input, output in self._inputs_and_mocked_outputs:
                if kwargs == _input:
                    return output

        raise Exception(f"No mocked output supplied for input: {kwargs}. Mocked inputs/outputs: {self._inputs_and_mocked_outputs}")

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "pk"


def test_read_nonexistent_stream_raises_exception(mocker):
    """Tests that attempting to sync a stream which the source does not return from the `streams` method raises an exception"""
    s1 = _MockStream(name="s1")
    s2 = _MockStream(name="this_stream_doesnt_exist_in_the_source")

    mocker.patch.object(_MockStream, "get_json_schema", return_value={})

    src = _MockSource(streams=[s1])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s2, SyncMode.full_refresh)])
    with pytest.raises(KeyError):
        list(src.read(logger, {}, catalog))


def test_read_nonexistent_stream_without_raises_exception(mocker):
    """Tests that attempting to sync a stream which the source does not return from the `streams` method raises an exception"""
    s1 = _MockStream(name="s1")
    s2 = _MockStream(name="this_stream_doesnt_exist_in_the_source")

    mocker.patch.object(_MockStream, "get_json_schema", return_value={})

    src = _MockSource(streams=[s1], exception_on_missing_stream=False)

    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s2, SyncMode.full_refresh)])
    messages = list(src.read(logger, {}, catalog))

    assert messages == []


def test_read_stream_emits_repository_message_on_error(mocker, message_repository):
    stream = _MockStream(name="my_stream")
    mocker.patch.object(_MockStream, "get_json_schema", return_value={})
    mocker.patch.object(_MockStream, "read_records", side_effect=RuntimeError("error"))

    source = _MockSource(streams=[stream], message_repository=message_repository)

    with pytest.raises(RuntimeError):
        messages = list(source.read(logger, {}, ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])))
        assert MESSAGE_FROM_REPOSITORY in messages


def _configured_stream(stream: Stream, sync_mode: SyncMode):
    return ConfiguredAirbyteStream(
        stream=stream.as_airbyte_stream(),
        sync_mode=sync_mode,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
