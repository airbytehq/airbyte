#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from pathlib import Path

import pipelines.helpers.connectors.modifed
import pytest
from pipelines.airbyte_ci.steps import gradle
from pipelines.models import steps

pytestmark = [
    pytest.mark.anyio,
]


class TestGradleTask:
    class DummyStep(gradle.GradleTask):
        gradle_task_name = "dummyTask"
        title = "Dummy Step"

        async def _run(self) -> steps.StepResult:
            return steps.StepResult(step=self, status=steps.StepStatus.SUCCESS)

    @pytest.fixture
    def test_context(self, mocker, dagger_client):
        return mocker.Mock(
            secrets_to_mask=[],
            dagger_client=dagger_client,
            connector=pipelines.helpers.connectors.modifed.ConnectorWithModifiedFiles(
                "source-postgres", frozenset({Path("airbyte-integrations/connectors/source-postgres/metadata.yaml")})
            ),
        )

    async def test_build_include(self, test_context):
        step = self.DummyStep(test_context)
        assert step.build_include

    def test_params(self, test_context):
        step = self.DummyStep(test_context)
        step.extra_params = {"-x": ["dummyTask", "dummyTask2"]}
        assert set(step.params_as_cli_options) == {
            "-x=dummyTask",
            "-x=dummyTask2",
        }
