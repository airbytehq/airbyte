#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import (
    SubstreamPartitionRouter,
)
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class BingAdsCampaignsPartitionRouter(SubstreamPartitionRouter):
    """
    Custom router for Bing Ads campaigns to ensure both account_id 
    and customer_id are included in stream slices.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Generates stream slices from parent stream, ensuring each slice
        contains both account_id and customer_id values.
        """
        # Get the first config which should point to accounts_stream
        if not self.parent_stream_configs:
            yield from []
            return

        parent_config = self.parent_stream_configs[0]
        accounts_stream = parent_config.stream

        # Process each account from the accounts stream
        for accounts_slice in accounts_stream.stream_slices(
            sync_mode=SyncMode.full_refresh
        ):
            for account in accounts_stream.read_records(
                sync_mode=SyncMode.full_refresh, 
                stream_slice=accounts_slice
            ):
                # Create a slice with both account_id and customer_id
                partition: Dict[str, Any] = {
                    "account_id": account["Id"],
                    "customer_id": account["ParentCustomerId"]
                }
                yield StreamSlice(partition=partition, cursor_slice={})