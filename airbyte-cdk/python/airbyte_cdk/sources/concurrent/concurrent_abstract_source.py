#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from queue import Queue
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent.concurrent_stream_reader import ConcurrentStreamReader
from airbyte_cdk.sources.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.concurrent.queue_consumer import QueueConsumer


class Partition:
    pass


class ConcurrentAbstractSource(AbstractSource, ABC):
    def __init__(self, partitions_generator: PartitionGenerator, queue_consumer: QueueConsumer, queue: Queue, max_workers: int):
        self._stream_reader = ConcurrentStreamReader(partitions_generator, queue_consumer, queue, max_workers)

    # FIXME: can we safely replace Mappings with types?
    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        pass

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        pass

    def _get_num_dedicated_consumer_worker(self):
        return max(self._max_workers - 4, 1)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        # FIXME: what's the deal with the split config?
        # config, internal_config = split_config(config)
        stream_instances = {s.name: s for s in self.streams(config)}
        for configured_stream in catalog.streams:
            stream = stream_instances.get(configured_stream.stream.name)
            if not stream:
                raise ValueError("unexpected. needs to be handled!")  # FIXME
            # FIXME: I think this could be done async too...
            stream_is_available, reason = stream.check_availability(logger, self)
            if not stream_is_available:
                logger.warning(f"Skipped syncing stream '{stream.name}' because it was unavailable. {reason}")
                continue
            record_counter = 0
            for (record, stream) in self._stream_reader.read_stream(stream):
                record_counter += 1
                yield self._get_message(record, stream)
            print(f"Read {record_counter} records for {stream.name}")
