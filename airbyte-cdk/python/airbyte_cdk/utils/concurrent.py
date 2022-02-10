#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import math
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources.streams import Stream


class StopException(Exception):
    pass


@dataclass(order=True, frozen=True)
class Cursor:
    slice_number: Union[float, int]
    record_number: Union[float, int]


@dataclass(order=True, frozen=True)
class QueueMessage(Cursor):
    record: Optional[Dict] = field(compare=False, default=None)

    @property
    def cursor(self) -> Cursor:
        return Cursor(self.slice_number, self.record_number)

    def next_cursor(self) -> Cursor:
        if self.record is None:
            return Cursor(self.slice_number + 1, 1)
        return Cursor(self.slice_number, self.record_number + 1)


messageDone = QueueMessage(math.inf, math.inf)
messageFail = QueueMessage(0, 0)


class ConcurrentStreamReader:

    DELAY = 0.1

    def __init__(self, stream_instance: Stream, configured_stream: ConfiguredAirbyteStream):
        self.stream_instance = stream_instance
        self.max_workers = stream_instance.max_workers
        self.logger = stream_instance.logger
        self.configured_stream = configured_stream

        self.stop_all = threading.Event()
        self.to_workers: queue.Queue[QueueMessage] = queue.Queue(maxsize=self.max_workers * 100)
        self.to_consumer: queue.Queue[QueueMessage] = queue.PriorityQueue()
        self.cursor = Cursor(1, 1)
        self.delay: float = self.DELAY

    def __enter__(self):
        for _ in range(self.max_workers):
            threading.Thread(target=self._safe_thread, args=(self.worker,), daemon=True).start()
        threading.Thread(target=self._safe_thread, args=(self.producer,), daemon=True).start()
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
            self.to_consumer.put(messageFail)

    def _q_put(self, Q, message):
        while True:
            try:
                return Q.put(message, timeout=10)
            except queue.Full:
                pass
            finally:
                if self.stop_all.is_set():
                    raise StopException()

    def _q_get(self, Q):
        while True:
            try:
                return Q.get(timeout=10)
            except queue.Empty:
                pass
            finally:
                if self.stop_all.is_set():
                    raise StopException()

    def producer(self):
        slices = self.stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=self.configured_stream.cursor_field)
        for slice_number, slice in enumerate(slices, 1):
            q_message = QueueMessage(slice_number, 0, slice)
            self._q_put(self.to_workers, q_message)
        for _ in range(self.max_workers):
            self._q_put(self.to_workers, messageDone)

    def worker(self):
        while True:
            item = self._q_get(self.to_workers)
            if item == messageDone:
                self.to_consumer.put(messageDone)
                break

            slice = item.record
            records = self.stream_instance.read_records(
                stream_slice=slice, sync_mode=SyncMode.full_refresh, cursor_field=self.configured_stream.cursor_field
            )
            for record_number, record in enumerate(records, 1):
                q_message = QueueMessage(item.slice_number, record_number, record)
                self._q_put(self.to_consumer, q_message)
            q_message = QueueMessage(item.slice_number, record_number + 1)
            self._q_put(self.to_consumer, q_message)

    def __iter__(self):
        stopped_workers = 0
        while True:
            item = self.to_consumer.get(timeout=300)
            if item == messageDone:
                stopped_workers += 1
                if stopped_workers >= self.max_workers:
                    return
            elif item == messageFail:
                return
            else:
                if not self.is_next(item):
                    self.to_consumer.put(item)
                elif item.record:
                    yield item.record

    def is_next(self, q_message: QueueMessage) -> bool:
        if q_message.cursor == self.cursor:
            self.delay = self.DELAY
            self.cursor = q_message.next_cursor()
            return True

        self.delay = self.delay * 2
        time.sleep(self.delay)
        return False
