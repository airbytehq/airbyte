#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Optional, Tuple

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import GradleTask, StepResult, StepStatus
from ci_connector_ops.pipelines.builds.common import BuildConnectorImageBase
from dagger import Container, File, QueryError


class BuildConnectorImage(BuildConnectorImageBase, GradleTask):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    gradle_task_name = "distTar"

    async def build_tar(self) -> File:
        distTar = (
            environments.with_gradle(
                self.context,
                self.build_include,
                docker_service_name=self.docker_service_name,
                bind_to_docker_host=self.BIND_TO_DOCKER_HOST,
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            .with_exec(self._get_gradle_command())
            .with_workdir(f"{self.context.connector.code_directory}/build/distributions")
        )

        distributions = await distTar.directory(".").entries()
        tar_files = [f for f in distributions if f.endswith(".tar")]
        if len(tar_files) > 1:
            raise Exception(
                "The distributions directory contains multiple connector tar files. We can't infer which one should be used. Please review and delete any unnecessary tar files."
            )
        return distTar.file(tar_files[0])

    async def _run(self) -> Tuple[StepResult, Optional[Container]]:
        try:
            tar_file = await self.build_tar()
            java_connector = await environments.with_airbyte_java_connector(self.context, tar_file, self.build_platform)
            step_result = await self.get_step_result(java_connector.with_exec(["spec"]))
            return step_result, java_connector
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None
