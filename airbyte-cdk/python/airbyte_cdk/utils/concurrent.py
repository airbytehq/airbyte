#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import queue
import threading
from enum import Enum

from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources.streams import Stream


class Message(Enum):
    DONE = "DONE"
    FAIL = "FAIL"


class ConcurrentStreamReader:
    def __init__(self, stream_instance: Stream, configured_stream: ConfiguredAirbyteStream):
        self.stream_instance = stream_instance
        self.max_workers = stream_instance.max_workers
        self.logger = stream_instance.logger
        self.configured_stream = configured_stream

        self.stop_all = threading.Event()
        self.producer_to_worker = queue.Queue()
        self.worker_to_consumer = queue.Queue()

    def __enter__(self):
        for _ in range(self.max_workers):
            threading.Thread(target=self.worker, daemon=True).start()
        threading.Thread(target=self.producer, daemon=True).start()
        return self

    def __exit__(self, exc, value, tb):
        self.stop_all.set()

    def producer(self):
        try:
            slices = self.stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=self.configured_stream.cursor_field)
            for slice in slices:
                self.producer_to_worker.put(slice)
                if self.stop_all.is_set():
                    return
            for _ in range(self.max_workers):
                self.producer_to_worker.put(Message.DONE)
        except Exception as e:
            self.logger.exception(e)
            self.worker_to_consumer.put(Message.FAIL)

    def worker(self):
        try:
            while True:
                if self.stop_all.is_set():
                    return

                try:
                    item = self.producer_to_worker.get(timeout=10)
                except queue.Empty:
                    continue

                if isinstance(item, Message) and item == Message.DONE:
                    self.worker_to_consumer.put(Message.DONE)
                    break

                slice = item
                records = self.stream_instance.read_records(
                    stream_slice=slice, sync_mode=SyncMode.full_refresh, cursor_field=self.configured_stream.cursor_field
                )
                for record in records:
                    self.worker_to_consumer.put(record)
                    if self.stop_all.is_set():
                        return
        except Exception as e:
            self.logger.exception(e)
            self.worker_to_consumer.put(Message.FAIL)

    def __iter__(self):
        stopped_workers = 0
        while True:
            item = self.worker_to_consumer.get(timeout=300)
            if isinstance(item, Message):
                if item == Message.DONE:
                    stopped_workers += 1
                    if stopped_workers >= self.max_workers:
                        return
                elif item == Message.FAIL:
                    return
            else:
                yield item
