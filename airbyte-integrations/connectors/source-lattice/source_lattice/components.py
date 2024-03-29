from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
# from airbyte_cdk.sources.declarative.types import StreamSlice  # noqa: E501


@dataclass
class DedupedIdSubstreamPartitionRouter(SubstreamPartitionRouter):

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        # id_set = set[str]()
        for slice in super().stream_slices():
            print(f"The slice is {slice}")
            yield slice
