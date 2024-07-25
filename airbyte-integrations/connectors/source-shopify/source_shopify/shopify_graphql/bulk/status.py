# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from enum import Enum


class ShopifyBulkJobStatus(Enum):
    CREATED = "CREATED"
    CANCELED = "CANCELED"
    CANCELING = "CANCELING"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"
