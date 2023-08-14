#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import pytest
from pipelines import bases, contexts, gradle
from pipelines.actions import environments

pytestmark = [
    pytest.mark.anyio,
]


class TestGradleTask:
    class DummyStep(gradle.GradleTask):
        gradle_task_name = "dummyTask"

        async def _run(self) -> bases.StepResult:
            return bases.StepResult(self, bases.StepStatus.SUCCESS)

    @pytest.fixture
    async def test_context(self, tmpdir, dagger_client):
        context = contexts.ConnectorContext(
            pipeline_name="test",
            is_local=True,
            git_branch="test",
            git_revision="test",
            report_output_prefix=str(tmpdir),
            connector=bases.ConnectorWithModifiedFiles(
                "source-postgres", frozenset({Path("airbyte-integrations/connectors/source-postgres/metadata.yaml")})
            ),
        )
        context.dagger_client = dagger_client
        context.dockerd_service = await environments.with_dockerd_service(context)
        context.dockerd_service_name = "test-docker-host"
        return context

    async def test_build_include(self, test_context):
        step = self.DummyStep(test_context)
        assert step.build_include

    @pytest.mark.slow
    async def test_gradle_container(self, test_context):
        step = self.DummyStep(test_context)
        container = step.gradle_container
        assert await container.env_variable("TESTCONTAINERS_RYUK_DISABLED") == "true"
        assert await container.env_variable("TESTCONTAINERS_HOST_OVERRIDE") == test_context.dockerd_service_name
        assert await container.env_variable("DOCKER_HOST") == "tcp://test-docker-host:2375"
        assert (await container.with_exec(["pwd"]).stdout()).strip() == "/airbyte"
        container = container.with_mounted_directory(
            f"/airbyte/{str(test_context.connector.code_directory)}", await test_context.get_connector_dir()
        )
        assert (
            "BUILD SUCCESSFUL"
            in await container.with_exec(["./gradlew", "--dry-run", ":airbyte-integrations:connectors:source-postgres:test"]).stdout()
        )
