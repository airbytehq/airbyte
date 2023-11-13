#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import threading
from queue import Queue

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem

thread_local = threading.local()


class StreamReaderPool:
    def __init__(self, stream_readers):
        self.stream_readers = Queue(len(stream_readers))
        for stream_reader in stream_readers:
            self.stream_readers.put(stream_reader)

    def get_stream_reader(self):
        return self.stream_readers.get()

    def return_stream_reader(self, connection):
        self.stream_readers.put(connection)


class PartitionReader:
    """
    Generates records from a partition and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem], stream_reader_pool: StreamReaderPool) -> None:
        """
        :param queue: The queue to put the records in.
        """
        self._queue = queue
        self._stream_reader_pool = stream_reader_pool

    def _get_stream_reader(self) -> AbstractFileBasedStreamReader:
        if not hasattr(thread_local, "stream_reader"):
            self._set_stream_reader(self._stream_reader_pool.get_stream_reader())
        return thread_local.stream_reader

    def _set_stream_reader(self, stream_reader: AbstractFileBasedStreamReader) -> None:
        thread_local.stream_reader = stream_reader

    def process_partition(self, partition: Partition) -> None:
        """
        Process a partition and put the records in the output queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue.

        This method is meant to be called from a thread.
        :param partition: The partition to read data from
        :return: None
        """
        partition.stream_reader = self._get_stream_reader()
        try:
            for record in partition.read():
                self._queue.put(record)
            self._queue.put(PartitionCompleteSentinel(partition))
        except Exception as e:
            self._queue.put(e)
        finally:
            self._stream_reader_pool.return_stream_reader(thread_local.stream_reader)
            del thread_local.stream_reader
