#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

import dagger
from pipelines.dagger.actions.python.pipx import with_installed_pipx_package
from pipelines.dagger.containers.python import with_python_base
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import MountPath, Step, StepResult


class SimpleDockerStep(Step):
    def __init__(
        self,
        title: str,
        context: PipelineContext,
        paths_to_mount: List[MountPath] = [],
        internal_tools: List[MountPath] = [],
        secrets: dict[str, dagger.Secret] = {},
        env_variables: dict[str, str] = {},
        working_directory: str = "/",
        command: Optional[List[str]] = None,
    ):
        """A simple step that runs a given command in a container.

        Args:
            title (str): name of the step
            context (PipelineContext): context of the step
            paths_to_mount (List[MountPath], optional): directory paths to mount. Defaults to [].
            internal_tools (List[MountPath], optional): internal tools to install. Defaults to [].
            secrets (dict[str, dagger.Secret], optional): secrets to add to container. Defaults to {}.
            env_variables (dict[str, str], optional): env variables to set in container. Defaults to {}.
            working_directory (str, optional): working directory to run the command in. Defaults to "/".
            command (Optional[List[str]], optional): The default command to run. Defaults to None.
        """
        self.title = title
        super().__init__(context)

        self.paths_to_mount = paths_to_mount
        self.working_directory = working_directory
        self.internal_tools = internal_tools
        self.secrets = secrets
        self.env_variables = env_variables
        self.command = command

    def _mount_paths(self, container: dagger.Container) -> dagger.Container:
        for path_to_mount in self.paths_to_mount:
            if path_to_mount.optional and not path_to_mount.path.exists():
                continue

            path_string = str(path_to_mount)
            destination_path = f"/{path_string}"
            if path_to_mount.is_file:
                file_to_load = self.context.get_repo_file(path_string)
                container = container.with_mounted_file(destination_path, file_to_load)
            else:
                container = container.with_mounted_directory(destination_path, self.context.get_repo_dir(path_string))
        return container

    async def _install_internal_tools(self, container: dagger.Container) -> dagger.Container:
        for internal_tool in self.internal_tools:
            container = await with_installed_pipx_package(self.context, container, str(internal_tool))
        return container

    def _set_workdir(self, container: dagger.Container) -> dagger.Container:
        return container.with_workdir(self.working_directory)

    def _set_env_variables(self, container: dagger.Container) -> dagger.Container:
        for key, value in self.env_variables.items():
            container = container.with_env_variable(key, value)
        return container

    def _set_secrets(self, container: dagger.Container) -> dagger.Container:
        for key, value in self.secrets.items():
            container = container.with_secret_variable(key, value)
        return container

    async def init_container(self) -> dagger.Container:
        # TODO (ben): Replace with python base container when available
        container = with_python_base(self.context)

        container = self._mount_paths(container)
        container = self._set_env_variables(container)
        container = self._set_secrets(container)
        container = await self._install_internal_tools(container)
        container = self._set_workdir(container)

        return container

    async def _run(self, command=None) -> StepResult:
        command_to_run = command or self.command
        if not command_to_run:
            raise ValueError(f"No command given to the {self.title} step")

        container_to_run = await self.init_container()
        return await self.get_step_result(container_to_run.with_exec(command_to_run))
