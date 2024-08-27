# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.models.declarative_component_schema import AsyncJobStatusMap as AsyncJobStatusMapModel


class AsyncJobStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class AsyncJobStatusMap:
    model: AsyncJobStatusMapModel
    parameters: InitVar[Mapping[str, Any]]

    def parse_input(self) -> Mapping[str, AsyncJobStatus]:
        processed_mapping = {}
        for key, value in self.model.dict().items():
            if key == "running":
                processed_mapping[value] = AsyncJobStatus.RUNNING
            elif key == "completed":
                processed_mapping[value] = AsyncJobStatus.COMPLETED
            elif key == "failed":
                processed_mapping[value] = AsyncJobStatus.FAILED
            elif key == "timeout":
                processed_mapping[value] = AsyncJobStatus.TIMED_OUT
        return processed_mapping
