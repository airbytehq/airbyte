#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

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

        async def _run(self) -> steps.StepResult:
            return steps.StepResult(self, steps.StepStatus.SUCCESS)

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
