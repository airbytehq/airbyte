#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.incremental.concurrent_partition_cursor import (
    ConcurrentCursorFactory,
    ConcurrentPerPartitionCursor,
)

__all__ = [
    "ConcurrentCursorFactory",
    "ConcurrentPerPartitionCursor",
]
