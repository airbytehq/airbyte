#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any

from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import Step, StepResult, StepStatus


class NoOpStep(Step):
    """A step that does nothing."""

    title = "No Op"
    should_log = False

    def __init__(self, context: PipelineContext, step_status: StepStatus) -> None:
        super().__init__(context)
        self.step_status = step_status

    async def _run(self, *args: Any, **kwargs: Any) -> StepResult:
        return StepResult(step=self, status=self.step_status)
