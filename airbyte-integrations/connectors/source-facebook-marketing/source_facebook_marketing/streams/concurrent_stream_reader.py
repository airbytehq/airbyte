import itertools
import logging
import queue
import threading
import typing
from dataclasses import dataclass
from functools import total_ordering
from typing import Callable, ClassVar, Dict, List, Mapping, Any

from airbyte_protocol.models import SyncMode
from airbyte_cdk.models import ConfiguredAirbyteStream
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


class StopException(Exception):
    pass


@total_ordering
class Message:
    prio = 2
    number = 0
    counter = itertools.count()

    def __eq__(self, other):
        if not isinstance(other, Message):
            return TypeError
        return (self.prio, self.number) == (other.prio, other.number)

    def __lt__(self, other):
        if not isinstance(other, Message):
            return TypeError
        return (self.prio, self.number) < (other.prio, other.number)

    def set_number(self):
        self.number = next(self.counter)
        return self


@dataclass(eq=False)
class MessageDone(Message):
    pass


@dataclass(eq=False)
class MessageFail(Message):
    prio: ClassVar[int] = 1
    exception: Exception


@dataclass(eq=False)
class MessageSlice(Message):
    slice: Mapping[str, Any] | None


@dataclass(eq=False)
class MessageData(Message):
    record: Dict


class ConcurrentStreamReader:
    TIMEOUT = 10

    def __init__(self, stream_instance: Stream,
                 max_workers: int,
                 logger: logging.Logger,
                 slice_logger: SliceLogger,
                 stream_state: typing.MutableMapping[str, typing.Any],
                 state_manager,
                 configured_stream: ConfiguredAirbyteStream):
        self.stream_instance = stream_instance
        self.state_manager = state_manager
        self.max_workers = max_workers
        self.logger = logger
        self.slice_logger = slice_logger
        self.configured_stream = configured_stream
        self.stream_state = stream_state

        self.stop_all = threading.Event()
        self.to_workers: queue.Queue[Message] = queue.Queue(maxsize=self.max_workers * 100)
        self.to_consumer: queue.Queue[Message] = queue.Queue()
        self.to_iterator: queue.Queue[Message] = queue.PriorityQueue()

        self.has_slices = False

        self.threads: List[threading.Thread] = []
        self.threads.append(threading.Thread(target=self._safe_thread, args=(self.consumer,), daemon=True))
        for _ in range(self.max_workers):
            self.threads.append(threading.Thread(target=self._safe_thread, args=(self.worker,), daemon=True))
        self.threads.append(threading.Thread(target=self._safe_thread, args=(self.producer,), daemon=True))

    def __enter__(self):
        for t in self.threads:
            t.start()
        return self

    def __exit__(self, exc, value, tb):
        self.stop_all.set()

    def _safe_thread(self, t: Callable):
        try:
            t()
        except StopException:
            pass
        except Exception as e:
            self.logger.exception(e)
            self.to_iterator.put(MessageFail(exception=e).set_number())

    def _q_put(self, Q, message):
        while True:
            try:
                return Q.put(message, timeout=self.TIMEOUT)
            except queue.Full:
                pass
            finally:
                if self.stop_all.is_set():
                    raise StopException()

    def _q_get(self, Q):
        while True:
            try:
                return Q.get(timeout=self.TIMEOUT)
            except queue.Empty:
                pass
            finally:
                if self.stop_all.is_set():
                    raise StopException()

    def producer(self):
        slices = self.stream_instance.stream_slices(sync_mode=self.configured_stream.sync_mode,
                                                    cursor_field=self.configured_stream.cursor_field)
        self.stream_instance.logger.debug(f"Processing stream slices for {self.stream_instance.name} "
                                          f"(sync_mode: {self.configured_stream.sync_mode.name}, "
                                          f"cursor_field: {self.configured_stream.cursor_field})",
                                          extra={"stream_slices": slices})
        for slice in slices:
            self._q_put(self.to_consumer, MessageSlice(slice=slice))
            Q = queue.Queue()
            message = MessageData(record={"queue": Q, "slice": slice})
            self._q_put(self.to_workers, message)
            self._q_put(self.to_consumer, message)
        for _ in range(self.max_workers):
            self._q_put(self.to_workers, MessageDone())
        self._q_put(self.to_consumer, MessageDone())

    def worker(self):
        while True:
            message = self._q_get(self.to_workers)
            if isinstance(message, MessageDone):
                break
            queue, slice = message.record["queue"], message.record["slice"]
            records = self.stream_instance.read_records(
                stream_slice=slice,
                sync_mode=self.configured_stream.sync_mode,
                stream_state=self.stream_state,
                cursor_field=self.configured_stream.cursor_field
            )
            for record in records:
                self._q_put(queue, MessageData(record=record))
            self._q_put(queue, MessageDone())

    def consumer(self):
        while True:
            message = self._q_get(self.to_consumer)
            if isinstance(message, MessageDone):
                self._q_put(self.to_iterator, message.set_number())
                break
            if isinstance(message, MessageSlice):
                self._q_put(self.to_iterator, message)
                continue
            queue = message.record["queue"]
            while True:
                message = self._q_get(queue)
                if isinstance(message, MessageDone):
                    break
                self._q_put(self.to_iterator, message.set_number())

    def __iter__(self):
        while True:
            message = self.to_iterator.get()
            if isinstance(message, MessageSlice):
                if self.slice_logger.should_log_slice_message(self.logger):
                    yield self.slice_logger.create_slice_log_message(message.slice)
                continue
            if isinstance(message, MessageDone):
                break
            if isinstance(message, MessageFail):
                raise message.exception
            self.stream_state = self.stream_instance.get_updated_state(self.stream_state, message.record)
            if self.configured_stream.sync_mode == SyncMode.incremental:
                checkpoint_interval = self.stream_instance.state_checkpoint_interval
                if checkpoint_interval and message.number % checkpoint_interval == 0:
                    airbyte_state_message = self.stream_instance._checkpoint_state(self.stream_state, self.state_manager)
                    yield airbyte_state_message
            self.has_slices = True
            yield message.record
