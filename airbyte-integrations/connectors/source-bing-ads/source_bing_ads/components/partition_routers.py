#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class SubstreamDedupPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        For migration to manifest connector we needed to migrate legacy state to per partition
        but regular SubstreamPartitionRouter will include the parent_slice in the partition that
        LegacyToPerPartitionStateMigration can't add in transformed state.
        Then, we remove the parent_slice and also deduplicate partitions.
        """
        stream_slices = super().stream_slices()
        seen_keys = set()
        for stream_slice in stream_slices:
            stream_slice_partition: Dict[str, Any] = dict(stream_slice.partition)
            partition_keys = list(stream_slice_partition.keys())
            if "parent_slice" in partition_keys:
                partition_keys.remove("parent_slice")
                stream_slice_partition.pop("parent_slice", None)
            if len(partition_keys) != 1:
                raise ValueError(f"SubstreamDedupPartitionRouter expects a single partition key-value pair. Got {stream_slice_partition}")

            # deduplicate by partition key
            key = stream_slice_partition[partition_keys[0]]
            if key in seen_keys:
                continue
            seen_keys.add(key)

            yield StreamSlice(
                partition=stream_slice_partition,
                cursor_slice=stream_slice.cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )
