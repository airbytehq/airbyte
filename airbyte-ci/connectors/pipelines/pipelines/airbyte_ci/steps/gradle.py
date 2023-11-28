#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import ClassVar

import pipelines.dagger.actions.system.docker
from pipelines.dagger.actions import secrets
from pipelines.dagger.actions.gradle import GradleTaskExecutor
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import Step, StepResult


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        title (str): The step title.
        gradle_task_name (str): The Gradle task name to run.
        bind_to_docker_host (bool): Whether to install the docker client and bind it to the host.
        mount_connector_secrets (bool): Whether to mount connector secrets.
    """

    gradle_task_name: ClassVar[str]
    bind_to_docker_host: ClassVar[bool] = False
    mount_connector_secrets: ClassVar[bool] = False

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:
        async with GradleTaskExecutor(
            self.context.dagger_client,
            self.context.get_repo_dir("."),
            self.context.is_local,
            build_cdk=True,
            workdir="/airbyte",
            s3_build_cache_access_key_id=self.context.s3_build_cache_access_key_id_secret,
            s3_build_cache_secret_key=self.context.s3_build_cache_secret_key_secret,
        ) as task_executor:
            # From this point on, we add layers which are task-dependent.
            if self.mount_connector_secrets:
                secrets_dir = f"{self.context.connector.code_directory}/secrets"
                task_executor.gradle_container = task_executor.gradle_container.with_(
                    await secrets.mounted_connector_secrets(self.context, secrets_dir)
                )
            if self.bind_to_docker_host:
                # If this GradleTask subclass needs docker, then install it and bind it to the existing global docker host container.
                task_executor.gradle_container = pipelines.dagger.actions.system.docker.with_bound_docker_host(
                    self.context, task_executor.gradle_container
                )
                # This installation should be cheap, as the package has already been downloaded, and its dependencies are already installed.
                task_executor.gradle_container = task_executor.gradle_container.with_exec(["yum", "install", "-y", "docker"])

            connector_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
            await task_executor.run_task(connector_task, f"-Ds3BuildCachePrefix={self.context.connector.technical_name}")

        return await self.get_step_result(task_executor.gradle_container)
