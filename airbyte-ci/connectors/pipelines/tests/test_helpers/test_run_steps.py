# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time

import anyio
import pytest
from pipelines.helpers.run_steps import RunStepOptions, StepToRun, run_steps
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import Step, StepResult, StepStatus

test_context = PipelineContext(pipeline_name="test", is_local=True, git_branch="test", git_revision="test")


class TestStep(Step):
    title = "Test Step"

    async def _run(self, result_status=StepStatus.SUCCESS) -> StepResult:
        return StepResult(self, result_status)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "desc, steps, expected_results, options",
    [
        (
            "All consecutive steps succeed",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [StepToRun(id="step2", step=TestStep(test_context))],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [StepToRun(id="step4", step=TestStep(test_context))],
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.SUCCESS, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=True),
        ),
        (
            "Steps all succeed with parallel steps",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [
                    StepToRun(id="step2", step=TestStep(test_context)),
                    StepToRun(id="step3", step=TestStep(test_context)),
                ],
                [StepToRun(id="step4", step=TestStep(test_context))],
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.SUCCESS, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=True),
        ),
        (
            "Steps after a failed step are skipped, when fail_fast is True",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [StepToRun(id="step2", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE})],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [StepToRun(id="step4", step=TestStep(test_context))],
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.FAILURE, "step3": StepStatus.SKIPPED, "step4": StepStatus.SKIPPED},
            RunStepOptions(fail_fast=True),
        ),
        (
            "Steps after a failed step are not skipped, when fail_fast is False",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [StepToRun(id="step2", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE})],
                [StepToRun(id="step3", step=TestStep(test_context))],
                [StepToRun(id="step4", step=TestStep(test_context))],
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.FAILURE, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=False),
        ),
        (
            "fail fast has no effect on parallel steps",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [
                    StepToRun(id="step2", step=TestStep(test_context)),
                    StepToRun(id="step3", step=TestStep(test_context)),
                ],
                [StepToRun(id="step4", step=TestStep(test_context))],
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.SUCCESS, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=False),
        ),
        (
            "Nested parallel steps execute properly",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [
                    [StepToRun(id="step2", step=TestStep(test_context))],
                    [StepToRun(id="step3", step=TestStep(test_context))],
                    [
                        StepToRun(id="step4", step=TestStep(test_context)),
                        StepToRun(id="step5", step=TestStep(test_context)),
                    ],
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
            RunStepOptions(fail_fast=True),
        ),
        (
            "When fail_fast is True, nested parallel steps skip at the first failure",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [
                    [StepToRun(id="step2", step=TestStep(test_context))],
                    [StepToRun(id="step3", step=TestStep(test_context))],
                    [
                        StepToRun(id="step4", step=TestStep(test_context)),
                        StepToRun(id="step5", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE}),
                    ],
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
            RunStepOptions(fail_fast=True),
        ),
        (
            "When fail_fast is False, nested parallel steps do not skip at the first failure",
            [
                [StepToRun(id="step1", step=TestStep(test_context))],
                [
                    [StepToRun(id="step2", step=TestStep(test_context))],
                    [StepToRun(id="step3", step=TestStep(test_context))],
                    [
                        StepToRun(id="step4", step=TestStep(test_context)),
                        StepToRun(id="step5", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE}),
                    ],
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
            RunStepOptions(fail_fast=False),
        ),
        (
            "When fail_fast is False, consecutive steps still operate as expected",
            [
                StepToRun(id="step1", step=TestStep(test_context)),
                StepToRun(id="step2", step=TestStep(test_context)),
                StepToRun(id="step3", step=TestStep(test_context)),
                StepToRun(id="step4", step=TestStep(test_context)),
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.SUCCESS, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=False),
        ),
        (
            "skip_steps skips the specified steps",
            [
                StepToRun(id="step1", step=TestStep(test_context)),
                StepToRun(id="step2", step=TestStep(test_context)),
                StepToRun(id="step3", step=TestStep(test_context)),
                StepToRun(id="step4", step=TestStep(test_context)),
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.SKIPPED, "step3": StepStatus.SUCCESS, "step4": StepStatus.SUCCESS},
            RunStepOptions(fail_fast=False, skip_steps=["step2"]),
        ),
        (
            "step is skipped if the dependency fails",
            [
                StepToRun(id="step1", step=TestStep(test_context)),
                StepToRun(id="step2", step=TestStep(test_context), args={"result_status": StepStatus.FAILURE}),
                StepToRun(id="step3", step=TestStep(test_context)),
                StepToRun(id="step4", step=TestStep(test_context), depends_on=["step2"]),
            ],
            {"step1": StepStatus.SUCCESS, "step2": StepStatus.FAILURE, "step3": StepStatus.SUCCESS, "step4": StepStatus.SKIPPED},
            RunStepOptions(fail_fast=False),
        ),
    ],
)
async def test_run_steps_output(desc, steps, expected_results, options):
    results = await run_steps(steps, options=options)

    for step_id, expected_status in expected_results.items():
        assert results[step_id].status == expected_status, desc


@pytest.mark.anyio
async def test_run_steps_concurrent():
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


@pytest.mark.anyio
async def test_run_steps_concurrency_of_1():
    ran_at = {}

    class SleepStep(Step):
        title = "Sleep Step"

        async def _run(self, name, sleep) -> StepResult:
            ran_at[name] = time.time()
            await anyio.sleep(sleep)
            return StepResult(self, StepStatus.SUCCESS)

    steps = [
        StepToRun(id="step1", step=SleepStep(test_context), args={"name": "step1", "sleep": 1}),
        StepToRun(id="step2", step=SleepStep(test_context), args={"name": "step2", "sleep": 1}),
        StepToRun(id="step3", step=SleepStep(test_context), args={"name": "step3", "sleep": 1}),
        StepToRun(id="step4", step=SleepStep(test_context), args={"name": "step4", "sleep": 1}),
    ]

    await run_steps(steps, options=RunStepOptions(concurrency=1))

    # Assert that they run sequentially
    assert ran_at["step1"] < ran_at["step2"]
    assert ran_at["step2"] < ran_at["step3"]
    assert ran_at["step3"] < ran_at["step4"]


@pytest.mark.anyio
async def test_run_steps_sequential():
    ran_at = {}

    class SleepStep(Step):
        title = "Sleep Step"

        async def _run(self, name, sleep) -> StepResult:
            await anyio.sleep(sleep)
            ran_at[name] = time.time()
            return StepResult(self, StepStatus.SUCCESS)

    steps = [
        [StepToRun(id="step1", step=SleepStep(test_context), args={"name": "step1", "sleep": 1})],
        [StepToRun(id="step1", step=SleepStep(test_context), args={"name": "step2", "sleep": 1})],
        [StepToRun(id="step3", step=SleepStep(test_context), args={"name": "step3", "sleep": 1})],
        [StepToRun(id="step4", step=SleepStep(test_context), args={"name": "step4", "sleep": 0})],
    ]

    await run_steps(steps)

    # assert that steps are run in order
    assert ran_at["step1"] < ran_at["step2"]
    assert ran_at["step2"] < ran_at["step3"]
    assert ran_at["step3"] < ran_at["step4"]


@pytest.mark.anyio
async def test_run_steps_passes_results():
    """
    Example pattern
        StepToRun(
            id=CONNECTOR_TEST_STEP_ID.INTEGRATION,
            step=IntegrationTests(context),
            args=_create_integration_step_args_factory(context),
            depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
        ),
        StepToRun(
            id=CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
            step=AcceptanceTests(context, True),
            args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output_artifact[LOCAL_BUILD_PLATFORM]},
            depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
        ),

    """

    class Simple(Step):
        title = "Test Step"

        async def _run(self, arg1, arg2) -> StepResult:
            output_artifact = f"{arg1}:{arg2}"
            return StepResult(self, StepStatus.SUCCESS, output_artifact=output_artifact)

    async def async_args(results):
        return {"arg1": results["step2"].output_artifact, "arg2": "4"}

    steps = [
        [StepToRun(id="step1", step=Simple(test_context), args={"arg1": "1", "arg2": "2"})],
        [StepToRun(id="step2", step=Simple(test_context), args=lambda results: {"arg1": results["step1"].output_artifact, "arg2": "3"})],
        [StepToRun(id="step3", step=Simple(test_context), args=async_args)],
    ]

    results = await run_steps(steps)

    assert results["step1"].output_artifact == "1:2"
    assert results["step2"].output_artifact == "1:2:3"
    assert results["step3"].output_artifact == "1:2:3:4"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_args",
    [
        1,
        True,
        "string",
        [1, 2],
        None,
    ],
)
async def test_run_steps_throws_on_invalid_args(invalid_args):
    steps = [
        [StepToRun(id="step1", step=TestStep(test_context), args=invalid_args)],
    ]

    with pytest.raises(TypeError):
        await run_steps(steps)
