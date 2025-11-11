#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class GroupingPartitionRouter(PartitionRouter):
    """
    A partition router that groups partitions from an underlying partition router into batches of a specified size.
    This is useful for APIs that support filtering by multiple partition keys in a single request.

    Attributes:
        group_size (int): The number of partitions to include in each group.
        underlying_partition_router (PartitionRouter): The partition router whose output will be grouped.
        deduplicate (bool): If True, ensures unique partitions within each group by removing duplicates based on the partition key.
        config (Config): The connector configuration.
        parameters (Mapping[str, Any]): Additional parameters for interpolation and configuration.
    """

    group_size: int
    underlying_partition_router: PartitionRouter
    config: Config
    deduplicate: bool = True

    def __post_init__(self) -> None:
        self._state: Optional[Mapping[str, StreamState]] = {}

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Lazily groups partitions from the underlying partition router into batches of size `group_size`.

        This method processes partitions one at a time from the underlying router, maintaining a batch buffer.
        When the buffer reaches `group_size` or the underlying router is exhausted, it yields a grouped slice.
        If deduplication is enabled, it tracks seen partition keys to ensure uniqueness within the current batch.

        Yields:
            Iterable[StreamSlice]: An iterable of StreamSlice objects, where each slice contains a batch of partition values.
        """
        batch = []
        seen_keys = set()

        # Iterate over partitions lazily from the underlying router
        for partition in self.underlying_partition_router.stream_slices():
            # Extract the partition key (assuming single key-value pair, e.g., {"board_ids": value})
            partition_keys = list(partition.partition.keys())
            # skip parent_slice as it is part of SubstreamPartitionRouter partition
            if "parent_slice" in partition_keys:
                partition_keys.remove("parent_slice")
            if len(partition_keys) != 1:
                raise ValueError(
                    f"GroupingPartitionRouter expects a single partition key-value pair. Got {partition.partition}"
                )
            key = partition.partition[partition_keys[0]]

            # Skip duplicates if deduplication is enabled
            if self.deduplicate and key in seen_keys:
                continue

            # Add partition to the batch
            batch.append(partition)
            if self.deduplicate:
                seen_keys.add(key)

            # Yield the batch when it reaches the group_size
            if len(batch) == self.group_size:
                self._state = self.underlying_partition_router.get_stream_state()
                yield self._create_grouped_slice(batch)
                batch = []  # Reset the batch

        self._state = self.underlying_partition_router.get_stream_state()
        # Yield any remaining partitions if the batch isn't empty
        if batch:
            yield self._create_grouped_slice(batch)

    def _create_grouped_slice(self, batch: list[StreamSlice]) -> StreamSlice:
        """
        Creates a grouped StreamSlice from a batch of partitions, aggregating extra fields into a dictionary with list values.

        Args:
            batch (list[StreamSlice]): A list of StreamSlice objects to group.

        Returns:
            StreamSlice: A single StreamSlice with combined partition and extra field values.
        """
        # Combine partition values into a single dict with lists
        grouped_partition = {
            key: [p.partition.get(key) for p in batch] for key in batch[0].partition.keys()
        }

        # Aggregate extra fields into a dict with list values
        extra_fields_dict = (
            {
                key: [p.extra_fields.get(key) for p in batch]
                for key in set().union(*(p.extra_fields.keys() for p in batch if p.extra_fields))
            }
            if any(p.extra_fields for p in batch)
            else {}
        )
        return StreamSlice(
            partition=grouped_partition,
            cursor_slice={},  # Cursor is managed by the underlying router or incremental sync
            extra_fields=extra_fields_dict,
        )

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """Delegate state retrieval to the underlying partition router."""
        return self._state
