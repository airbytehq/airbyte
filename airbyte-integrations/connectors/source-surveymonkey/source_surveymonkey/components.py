#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class SurveyIdPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:

        survey_ids = self.config.get("survey_ids", [])
        parent_stream_config = self.parent_stream_configs[0]
        parent_key = parent_stream_config.parent_key.string
        partition_field = parent_stream_config.partition_field.string

        if survey_ids:
            for item in survey_ids:
                yield {partition_field: item}
        else:
            for parent_stream_config in self.parent_stream_configs:
                for item in parent_stream_config.stream.read_records(sync_mode=SyncMode.full_refresh):
                    yield {partition_field: item[parent_key]}

        yield from []
