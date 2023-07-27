#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from datetime import timedelta

import anyio
import pytest
from pipelines import bases

pytestmark = [
    pytest.mark.anyio,
]


class TestStep:
    class DummyStep(bases.Step):
        title = "Dummy step"
        max_retries = 3
        max_duration = timedelta(seconds=2)

        async def _run(self, run_duration: timedelta) -> bases.StepResult:
            await anyio.sleep(run_duration.total_seconds())
            return bases.StepResult(self, bases.StepStatus.SUCCESS)

    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock(secrets_to_mask=[])

    async def test_run_with_timeout(self, test_context):
        step = self.DummyStep(test_context)
        step_result = await step.run(run_duration=step.max_duration - timedelta(seconds=1))
        assert step_result.status == bases.StepStatus.SUCCESS
        assert step.retry_count == 0

        step_result = await step.run(run_duration=step.max_duration + timedelta(seconds=1))
        timed_out_step_result = step._get_timed_out_step_result()
        assert step_result.status == timed_out_step_result.status
        assert step_result.stdout == timed_out_step_result.stdout
        assert step_result.stderr == timed_out_step_result.stderr
        assert step_result.output_artifact == timed_out_step_result.output_artifact
        assert step.retry_count == step.max_retries + 1


class TestReport:
    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock()

    def test_report_failed_if_it_has_no_step_result(self, test_context):
        report = bases.Report(test_context, [])
        assert not report.success
        report = bases.Report(test_context, [bases.StepResult(None, bases.StepStatus.FAILURE)])
        assert not report.success

        report = bases.Report(
            test_context, [bases.StepResult(None, bases.StepStatus.FAILURE), bases.StepResult(None, bases.StepStatus.SUCCESS)]
        )
        assert not report.success

        report = bases.Report(test_context, [bases.StepResult(None, bases.StepStatus.SUCCESS)])
        assert report.success

        report = bases.Report(
            test_context, [bases.StepResult(None, bases.StepStatus.SUCCESS), bases.StepResult(None, bases.StepStatus.SKIPPED)]
        )
        assert report.success

        report = bases.Report(test_context, [bases.StepResult(None, bases.StepStatus.SKIPPED)])
        assert report.success
