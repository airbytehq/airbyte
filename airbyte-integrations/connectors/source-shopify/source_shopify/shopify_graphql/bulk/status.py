#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from enum import Enum


class ShopifyBulkStatus(Enum):
    CREATED = "CREATED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"
