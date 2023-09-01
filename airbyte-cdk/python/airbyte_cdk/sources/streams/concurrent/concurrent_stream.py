# import concurrent
# import logging
# from concurrent.futures import Future
# from typing import Optional, List, Callable, Iterable, Mapping, Any
#
# from airbyte_protocol.models import SyncMode
#
# from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import AsyncIterator
# from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
# from airbyte_cdk.sources.streams.core import AbstractStream, StreamData
# from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
# from airbyte_cdk.sources.utils.slice_logger import SliceLogger
#
#
# class ConcurrentStream(AbstractStream):
#     def __init__(
#             self,
#             name,
#             partition_generator_provider: Callable[[], AsyncIterator],
#             partition_reader_provider: Callable[[], PartitionReader],
#             max_workers: int,
#     ):
#         self._partitions_generator_provider = partition_generator_provider
#         self._partition_reader_provider = partition_reader_provider
#         self._max_workers = max_workers
#         self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
#         self._name = name
#
#     def read_stream(
#             self, cursor_field: Optional[List[str]], logger: logging.Logger, slice_logger: SliceLogger, internal_config: InternalConfig = InternalConfig()
#     ) -> Iterable[StreamData]:
#         logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)")
#         total_records_counter = 0
#         futures = []
#         partition_generator = self._partitions_generator_provider()
#         partition_reader = self._partition_reader_provider()
#         # Submit partition generation tasks
#         partition_generator = AsyncIterator(lambda _: self.stream_slices)
#         futures.append(self._threadpool.submit(partition_generator.generate, self, SyncMode.full_refresh, cursor_field))
#         # While partitions are still being generated
#         while partition_generator.has_next() or partition_reader.has_next() or not self._is_done(futures):
#             self._check_for_errors(futures)
#
#             # While there is a partition to process
#             for record in partition_reader:
#                 yield record.stream_data
#             for partition in partition_generator:
#                 futures.append(self._threadpool.submit(partition_reader.process_partition, partition))
#                 if slice_logger.should_log_slice_message(logger):
#                     # FIXME: This is creating slice log messages for parity with the synchronous implementation
#                     # but these cannot be used by the connector builder to build slices because they can be unordered
#                     yield slice_logger.create_slice_log_message(partition._slice)
#         self._check_for_errors(futures)
#
#     def _is_done(self, futures: List[Future[Any]]) -> bool:
#         return all(future.done() for future in futures)
#
#     def _check_for_errors(self, futures: List[Future[Any]]) -> None:
#         exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
#         if exceptions_from_futures:
#             raise RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")
#
#     @property
#     def name(self) -> str:
#         """
#         :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
#         """
#         return self._name
