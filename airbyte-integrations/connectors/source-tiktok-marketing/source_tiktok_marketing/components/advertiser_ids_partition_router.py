# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Iterable

from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


class AdvertiserIdsPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        if self.config.get("credentials", {}).get("advertiser_id"):
            slices = [self.config["credentials"].get("advertiser_id")]
        else:
            slices = [_id.partition["advertiser_ids"] for _id in super().stream_slices()]

        start, end, step = 0, len(slices), 100

        for i in range(start, end, step):
            yield StreamSlice(partition={"advertiser_ids": json.dumps(slices[i : min(end, i + step)]), "parent_slice": {}}, cursor_slice={})


class AdvertiserIdPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        if self.config.get("credentials", {}).get("advertiser_id"):
            yield StreamSlice(
                partition={"advertiser_id": self.config["credentials"].get("advertiser_id"), "parent_slice": {}}, cursor_slice={}
            )
        else:
            yield from super().stream_slices()
