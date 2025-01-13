#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

import anyio
import pytest
from dagger import DaggerError

from pipelines.models import reports, steps

pytestmark = [
    pytest.mark.anyio,
]


class TestStep:
    class DummyStep(steps.Step):
        title = "Dummy step"
        max_retries = 3
        max_duration = timedelta(seconds=2)

        async def _run(self, run_duration: timedelta) -> steps.StepResult:
            await anyio.sleep(run_duration.total_seconds())
            return steps.StepResult(step=self, status=steps.StepStatus.SUCCESS)

    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock(secrets_to_mask=[])

    async def test_run_with_timeout(self, test_context):
        step = self.DummyStep(test_context)
        step_result = await step.run(run_duration=step.max_duration - timedelta(seconds=1))
        assert step_result.status == steps.StepStatus.SUCCESS
        assert step.retry_count == 0

        step_result = await step.run(run_duration=step.max_duration + timedelta(seconds=1))
        timed_out_step_result = step._get_timed_out_step_result()
        assert step_result.status == timed_out_step_result.status
        assert step_result.stdout == timed_out_step_result.stdout
        assert step_result.stderr == timed_out_step_result.stderr
        assert step_result.output == timed_out_step_result.output
        assert step.retry_count == step.max_retries + 1

    @pytest.mark.parametrize(
        "step_status, exc_info, max_retries, max_dagger_error_retries, expect_retry",
        [
            (steps.StepStatus.SUCCESS, None, 0, 0, False),
            (steps.StepStatus.SUCCESS, None, 3, 0, False),
            (steps.StepStatus.SUCCESS, None, 0, 3, False),
            (steps.StepStatus.SUCCESS, None, 3, 3, False),
            (steps.StepStatus.SKIPPED, None, 0, 0, False),
            (steps.StepStatus.SKIPPED, None, 3, 0, False),
            (steps.StepStatus.SKIPPED, None, 0, 3, False),
            (steps.StepStatus.SKIPPED, None, 3, 3, False),
            (steps.StepStatus.FAILURE, DaggerError(), 0, 0, False),
            (steps.StepStatus.FAILURE, DaggerError(), 0, 3, True),
            (steps.StepStatus.FAILURE, None, 0, 0, False),
            (steps.StepStatus.FAILURE, None, 0, 3, False),
            (steps.StepStatus.FAILURE, None, 3, 0, True),
        ],
    )
    async def test_run_with_retries(self, mocker, test_context, step_status, exc_info, max_retries, max_dagger_error_retries, expect_retry):
        step = self.DummyStep(test_context)
        step.max_dagger_error_retries = max_dagger_error_retries
        step.max_retries = max_retries
        step.max_duration = timedelta(seconds=60)
        step.retry_delay = timedelta(seconds=0)
        step._run = mocker.AsyncMock(
            side_effect=[steps.StepResult(step=step, status=step_status, exc_info=exc_info)]
            * (max(max_dagger_error_retries, max_retries) + 1)
        )

        step_result = await step.run()

        if expect_retry:
            assert step.retry_count > 0
        else:
            assert step.retry_count == 0
        assert step_result.status == step_status


class TestReport:
    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock()

    def test_report_failed_if_it_has_no_step_result(self, test_context):
        report = reports.Report(test_context, [])
        assert not report.success
        report = reports.Report(test_context, [steps.StepResult(step=None, status=steps.StepStatus.FAILURE)])
        assert not report.success

        report = reports.Report(
            test_context,
            [steps.StepResult(step=None, status=steps.StepStatus.FAILURE), steps.StepResult(step=None, status=steps.StepStatus.SUCCESS)],
        )
        assert not report.success

        report = reports.Report(test_context, [steps.StepResult(step=None, status=steps.StepStatus.SUCCESS)])
        assert report.success

        report = reports.Report(
            test_context,
            [steps.StepResult(step=None, status=steps.StepStatus.SUCCESS), steps.StepResult(step=None, status=steps.StepStatus.SKIPPED)],
        )
        assert report.success

        report = reports.Report(test_context, [steps.StepResult(step=None, status=steps.StepStatus.SKIPPED)])
        assert report.success
