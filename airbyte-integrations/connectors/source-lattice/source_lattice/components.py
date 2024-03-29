from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
# from airbyte_cdk.sources.declarative.types import StreamSlice  # noqa: E501


@dataclass
class DedupedIdSubstreamPartitionRouter(SubstreamPartitionRouter):

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        # This prevents us from making many duplicate requests
        id_set = set[str]()
        for stream_slice in super().stream_slices():
            if stream_slice["parent_id"] not in id_set:
                id_set.add(stream_slice["parent_id"])
                yield stream_slice
