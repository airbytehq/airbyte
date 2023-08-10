#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import pytest
from pipelines import bases, gradle

pytestmark = [
    pytest.mark.anyio,
]


class TestGradleTask:
    class DummyStep(gradle.GradleTask):
        gradle_task_name = "dummyTask"

        async def _run(self) -> bases.StepResult:
            return bases.StepResult(self, bases.StepStatus.SUCCESS)

    @pytest.fixture
    def test_context(self, mocker, dagger_client):
        return mocker.Mock(
            secrets_to_mask=[],
            dagger_client=dagger_client,
            connector=bases.ConnectorWithModifiedFiles(
                "source-postgres", frozenset({Path("airbyte-integrations/connectors/source-postgres/metadata.yaml")})
            ),
        )

    async def test_build_include(self, test_context):
        step = self.DummyStep(test_context)
        assert step.build_include
