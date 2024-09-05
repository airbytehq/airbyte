# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from enum import Enum


class AsyncJobStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
