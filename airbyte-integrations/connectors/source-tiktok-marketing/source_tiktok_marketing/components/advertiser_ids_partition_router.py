# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Iterable, Mapping

import dpath.util
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


class MultipleAdvertiserIdsPerPartition(SubstreamPartitionRouter):
    """
    Custom AdvertiserIdsPartitionRouter and AdvertiserIdPartitionRouter partition routers are used to get advertiser_ids
    as slices for streams where it uses as request param.

    When using a sandbox account, it's impossible to get advertiser_ids via API.
    In this case user need to provide advertiser_id in a config and connector need to use provided ids
    and do not make requests to get this id.

    When advertiser_id not provided components get slices as usual.
    Main difference between AdvertiserIdsPartitionRouter and AdvertiserIdPartitionRouter is
    that MultipleAdvertiserIdsPerPartition returns multiple advertiser_ids in a one slice when id is not provided,
    e.g. {"advertiser_ids": '["11111111", "22222222"]', "parent_slice": {}}.
    And SingleAdvertiserIdPerPartition returns single slice for every advertiser_id as usual.

    MultipleAdvertiserIdsPerPartition is used by Advertisers stream, which is full refresh only, where advertiser_ids is required param,
    this approach also helps make less amount of requests.
    Advertisers docs: https://business-api.tiktok.com/portal/docs?id=1739593083610113.

    path_in_config: List[List[str]]: path to value in the config in priority order.
    partition_field: str: field to insert partition value.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._path_to_partition_in_config = self._parameters["path_in_config"]
        self._partition_field = self._parameters["partition_field"]

    def get_partition_value_from_config(self) -> str:
        for path in self._path_to_partition_in_config:
            config_value = dpath.util.get(self.config, path, default=None)
            if config_value:
                return config_value

    def stream_slices(self) -> Iterable[StreamSlice]:
        partition_value_in_config = self.get_partition_value_from_config()
        if partition_value_in_config:
            slices = [partition_value_in_config]
        else:
            slices = [_id.partition[self._partition_field] for _id in super().stream_slices()]

        start, end, step = 0, len(slices), 100

        for i in range(start, end, step):
            yield StreamSlice(partition={"advertiser_ids": json.dumps(slices[i : min(end, i + step)]), "parent_slice": {}}, cursor_slice={})


class SingleAdvertiserIdPerPartition(MultipleAdvertiserIdsPerPartition):
    """
    SingleAdvertiserIdPerPartition returns single slice for every advertiser_id in the parent stream
    or takes value for advertiser_id from a config and skips reading slices.

    path_in_config: List[List[str]]: path to value in the config in priority order.
    partition_field: str: field to insert partition value.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        partition_value_in_config = self.get_partition_value_from_config()

        if partition_value_in_config:
            yield StreamSlice(partition={self._partition_field: partition_value_in_config, "parent_slice": {}}, cursor_slice={})
        else:
            yield from super(MultipleAdvertiserIdsPerPartition, self).stream_slices()
