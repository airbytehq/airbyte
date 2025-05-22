#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class SubstreamPartitionRouterSliceReducer(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """ "
        For migration to manifest connector we needed to migrate legacy state to per partition
        but regular SubstreamPartitionRouter will include stream_slice in the partition that
        LegacyToPerPartitionStateMigration won't include in transformed state.
        This is a workaround to remove it.
        """
        stream_slices = super().stream_slices()
        for stream_slice in stream_slices:
            stream_slice_partition = dict(stream_slice.partition)
            stream_slice_partition.pop("parent_slice", None)
            # todo: we may need to deduplicate accounts as they can appear for more tha one user
            yield StreamSlice(
                partition=stream_slice_partition,
                cursor_slice=stream_slice.cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )
