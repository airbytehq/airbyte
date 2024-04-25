#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class SurveyIdPartitionRouter(SubstreamPartitionRouter):
    """
    A SurveyIdPartitionRouter is specifically tailored for survey data, addressing the limitations of the current solution,
    SubstreamPartitionRouter, which only offers one option for partitioning via access to the parent stream with input.
    The SurveyIdPartitionRouter generates stream slices for partitioning based on either provided survey IDs or parent stream keys.


    Inherits from:
        SubstreamPartitionRouter

    Custom Methods:
        stream_slices: Generates stream slices for partitioning.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Generates stream slices for partitioning based on survey IDs or parent stream keys.
        """

        # Get the survey IDs from the configuration
        survey_ids = self.config.get("survey_ids", [])

        # Extract necessary configuration parameters
        parent_stream_config = self.parent_stream_configs[0]
        parent_key = parent_stream_config.parent_key.string
        partition_field = parent_stream_config.partition_field.string

        if survey_ids:
            # If specific survey IDs are provided, yield slices based on them
            for item in survey_ids:
                yield StreamSlice(partition={partition_field: item}, cursor_slice={})
        else:
            # If not, iterate over parent stream records and yield slices based on parent keys
            for parent_stream_config in self.parent_stream_configs:
                for item in parent_stream_config.stream.read_records(sync_mode=SyncMode.full_refresh):
                    yield StreamSlice(partition={partition_field: item[parent_key]}, cursor_slice={})

        # Ensures the function always returns an iterable
        yield from []
