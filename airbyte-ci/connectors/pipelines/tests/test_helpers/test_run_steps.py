import anyio
import pytest
import time
from pipelines.models.contexts import PipelineContext
from pipelines.models.steps import Step, StepResult, StepStatus
from pipelines.helpers.run_steps import RunStepOptions, StepToRun, run_steps

test_context = PipelineContext(
    pipeline_name="test",
    is_local=True,
    git_branch="test",
    git_revision="test"
)

class TestStep(Step):
    title = "Test Step"
    async def _run(self, result_status = StepStatus.SUCCESS) -> StepResult:
        return StepResult(self, result_status)

@pytest.mark.anyio
@pytest.mark.parametrize("steps, expected_results, options", [
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [StepToRun(id="step2", step=TestStep(test_context))],
            [StepToRun(id="step3", step=TestStep(test_context))],
            [StepToRun(id="step4", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [
                StepToRun(id="step2", step=TestStep(test_context)),
                StepToRun(id="step3", step=TestStep(test_context)),
            ],
            [StepToRun(id="step4", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [StepToRun(id="step2", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE})],
            [StepToRun(id="step3", step=TestStep(test_context))],
            [StepToRun(id="step4", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.FAILURE,
            "step3": StepStatus.SKIPPED,
            "step4": StepStatus.SKIPPED
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [StepToRun(id="step2", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE})],
            [StepToRun(id="step3", step=TestStep(test_context))],
            [StepToRun(id="step4", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.FAILURE,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS
        },
        RunStepOptions(fail_fast=False)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [
                StepToRun(id="step2", step=TestStep(test_context)),
                StepToRun(id="step3", step=TestStep(test_context)),
            ],
            [StepToRun(id="step4", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [
                [StepToRun(id="step2", step=TestStep(test_context))],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [
                    StepToRun(id="step4", step=TestStep(test_context)),
                    StepToRun(id="step5", step=TestStep(test_context)),
                ]
            ],
            [StepToRun(id="step6", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS,
            "step5": StepStatus.SUCCESS,
            "step6": StepStatus.SUCCESS,
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [
                [StepToRun(id="step2", step=TestStep(test_context))],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [
                    StepToRun(id="step4", step=TestStep(test_context)),
                    StepToRun(id="step5", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE}),
                ]
            ],
            [StepToRun(id="step6", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS,
            "step5": StepStatus.FAILURE,
            "step6": StepStatus.SKIPPED,
        },
        RunStepOptions(fail_fast=True)
    ),
    (
        [
            [StepToRun(id="step1", step=TestStep(test_context))],
            [
                [StepToRun(id="step2", step=TestStep(test_context))],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [
                    StepToRun(id="step4", step=TestStep(test_context)),
                    StepToRun(id="step5", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE}),
                ]
            ],
            [StepToRun(id="step6", step=TestStep(test_context))],
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS,
            "step5": StepStatus.FAILURE,
            "step6": StepStatus.SUCCESS,
        },
        RunStepOptions(fail_fast=False)
    ),
    (
        [
            StepToRun(id="step1", step=TestStep(test_context)),
            StepToRun(id="step2", step=TestStep(test_context)),
            StepToRun(id="step3", step=TestStep(test_context)),
            StepToRun(id="step4", step=TestStep(test_context)),
        ],
        {
            "step1": StepStatus.SUCCESS,
            "step2": StepStatus.SUCCESS,
            "step3": StepStatus.SUCCESS,
            "step4": StepStatus.SUCCESS
        },
        RunStepOptions(fail_fast=True)
    ),
])
async def test_run_steps_sequential(steps, expected_results, options):
    results = await run_steps(steps, options=options)

    for step_id, expected_status in expected_results.items():
        assert results[step_id].status == expected_status

@pytest.mark.anyio
async def test_run_steps_concurrency():
    ran_at = {}
    class SleepStep(Step):
        title = "Sleep Step"
        async def _run(self, name, sleep) -> StepResult:
            await anyio.sleep(sleep)
            ran_at[name] = time.time()
            return StepResult(self, StepStatus.SUCCESS)

    steps = [
        StepToRun(id="step1", step=SleepStep(test_context), args={"name": "step1", "sleep": 2}),
        StepToRun(id="step2", step=SleepStep(test_context), args={"name": "step2", "sleep": 2}),
        StepToRun(id="step3", step=SleepStep(test_context), args={"name": "step3", "sleep": 2}),
        StepToRun(id="step4", step=SleepStep(test_context), args={"name": "step4", "sleep": 0}),
    ]

    await run_steps(steps)

    # assert that step4 is the first step to finish
    assert ran_at["step4"] < ran_at["step1"]
    assert ran_at["step4"] < ran_at["step2"]
    assert ran_at["step4"] < ran_at["step3"]
