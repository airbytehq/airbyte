#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest

from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.helpers.utils import get_exec_result
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import MountPath

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
        diffed_branch="test",
        git_repo_url="test",
        report_output_prefix="test",
    )
    context.dagger_client = dagger_client
    return context


class TestSimpleDockerStep:
    async def test_env_variables_set(self, context):
        # Define test inputs
        title = "test_env_variables_set"
        env_variables = {"VAR1": "value1", "VAR2": "value2"}

        # Create SimpleDockerStep instance
        step = SimpleDockerStep(title=title, context=context, env_variables=env_variables)

        # Initialize container
        container = await step.init_container()

        # Check if environment variables are set
        for key, expected_value in env_variables.items():
            stdout_value = await container.with_exec(["printenv", key], use_entrypoint=True).stdout()
            actual_value = stdout_value.strip()
            assert actual_value == expected_value

    async def test_mount_paths(self, context):
        # Define test inputs
        title = "test_mount_paths"

        path_to_current_file = Path(__file__).relative_to(Path.cwd())
        invalid_path = Path("invalid_path")
        paths_to_mount = [
            MountPath(path=path_to_current_file, optional=False),
            MountPath(path=invalid_path, optional=True),
        ]

        # Create SimpleDockerStep instance
        step = SimpleDockerStep(title=title, context=context, paths_to_mount=paths_to_mount)

        # Initialize container
        container = await step.init_container()

        for path_to_mount in paths_to_mount:
            exit_code, _stdout, _stderr = await get_exec_result(
                container.with_exec(["test", "-f", f"{str(path_to_mount)}"], use_entrypoint=True)
            )

            expected_exit_code = 1 if path_to_mount.optional else 0
            assert exit_code == expected_exit_code

    async def test_invalid_mount_paths(self):
        path_to_current_file = Path(__file__).relative_to(Path.cwd())
        invalid_path = Path("invalid_path")

        # No errors expected
        MountPath(path=path_to_current_file, optional=False)
        MountPath(path=invalid_path, optional=True)

        # File not found error expected
        with pytest.raises(FileNotFoundError):
            MountPath(path=invalid_path, optional=False)

    async def test_work_dir(self, context):
        # Define test inputs
        title = "test_work_dir"
        working_directory = "/test"

        # Create SimpleDockerStep instance
        step = SimpleDockerStep(title=title, context=context, working_directory=working_directory)

        # Initialize container
        container = await step.init_container()

        # Check if working directory is set
        stdout_value = await container.with_exec(["pwd"], use_entrypoint=True).stdout()
        actual_value = stdout_value.strip()
        assert actual_value == working_directory
