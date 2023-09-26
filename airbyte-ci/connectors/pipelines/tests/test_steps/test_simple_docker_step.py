import os
from unittest.mock import MagicMock

import pytest

from pipelines.contexts import PipelineContext
from pipelines.steps.simple_docker_step import SimpleDockerStep, MountPath

pytestmark = [
    pytest.mark.anyio,
]

@pytest.fixture
def context(dagger_client):
    context = PipelineContext(
        pipeline_name="test",
        is_local=True,
        git_branch="test",
        git_revision="test",
    )
    context.dagger_client = dagger_client
    return context

class TestSimpleDockerStep:

    async def test_env_variables_set(self, context):
        # Define test inputs
        title = "test"
        context = context
        env_variables = {"VAR1": "value1", "VAR2": "value2"}

        # Create SimpleDockerStep instance
        step = SimpleDockerStep(title=title, context=context, env_variables=env_variables)

        # Initialize container
        container = await step.init_container()

        # Check if environment variables are set
        for key, expected_value in env_variables.items():
            stdout_value = await container.with_exec(["printenv", key]).stdout()
            actual_value = stdout_value.strip()
            assert actual_value == expected_value

