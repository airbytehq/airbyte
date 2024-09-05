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
        """
        Parses the input and returns a mapping of status values.

        Returns:
            A mapping of status values where the keys are the input values and the values are the corresponding AsyncJobStatus.

        Example:
            {
                'running': AsyncJobStatus.RUNNING,
                'completed': AsyncJobStatus.COMPLETED,
                'failed': AsyncJobStatus.FAILED,
                'timeout': AsyncJobStatus.TIMED_OUT,
            }
        """
        status_mapping = {}
        for key, value in self.model.dict().items():
            match key:
                case "running":
                    status_mapping[value] = AsyncJobStatus.RUNNING
                case "completed":
                    status_mapping[value] = AsyncJobStatus.COMPLETED
                case "failed":
                    status_mapping[value] = AsyncJobStatus.FAILED
                case "timeout":
                    status_mapping[value] = AsyncJobStatus.TIMED_OUT
        return status_mapping
