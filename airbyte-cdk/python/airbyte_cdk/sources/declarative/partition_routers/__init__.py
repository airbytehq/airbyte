#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter

__all__ = ["ListPartitionRouter", "SinglePartitionRouter", "SubstreamPartitionRouter"]
