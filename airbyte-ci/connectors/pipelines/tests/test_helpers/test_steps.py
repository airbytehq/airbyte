import pytest
from pipelines.models.contexts import PipelineContext
from pipelines.models.steps import Step, StepResult, StepStatus
from pipelines.helpers.steps import RunStepOptions, StepToRun, run_steps


@pytest.mark.anyio
async def test_run_steps():
    class TestStep(Step):
        async def _run(self) -> StepResult:
            return StepResult(self, StepStatus.SUCCESS)

    context = PipelineContext(
        pipeline_name="test",
        is_local=True,
        git_branch="test",
        git_revision="test"
    )

    steps = [
        StepToRun(id="step1", step=TestStep(context)),
        [
            StepToRun(id="step2", step=TestStep(context)),
            StepToRun(id="step3", step=TestStep(context)),
        ],
        StepToRun(id="step4", step=TestStep(context)),
    ]

    results = await run_steps(steps, options=RunStepOptions(fail_fast=False))

    assert results["step1"].status == StepStatus.SUCCESS
    assert results["step2"].status == StepStatus.SUCCESS
    assert results["step3"].status == StepStatus.SUCCESS
    assert results["step4"].status == StepStatus.SUCCESS
