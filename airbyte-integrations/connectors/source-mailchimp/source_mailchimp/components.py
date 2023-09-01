#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice



@dataclass
class CampaignIdPartitionRouter(SubstreamPartitionRouter):

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Iterate over each parent stream's record and create a StreamSlice for each record.
        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each record.
        yield a stream slice for each such records.
        If a parent slice contains no record, emit a slice with parent_record=None.
        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """

        campaign_stream = self.parent_stream_configs[0].stream
        if self.config.campaign_id:
            # this is a workaround to speed up SATs and enable incremental tests
            campaigns = [{"id": self.config.campaign_id}]
        else:
            campaigns = campaign_stream.read_records(sync_mode=SyncMode.full_refresh)
        for campaign in campaigns:
            slice_ = {"campaign_id": campaign["id"]}
            yield slice_

