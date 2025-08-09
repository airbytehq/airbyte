#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import Container, Directory, File, Platform, QueryError

from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.steps.gradle import GradleTask
from pipelines.dagger.containers import java
from pipelines.models.steps import StepResult, StepStatus


class BuildConnectorDistributionTar(GradleTask):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    title = "Build connector tar"
    gradle_task_name = "distTar"


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build Java connector images using the distTar Gradle task.
    """

    async def _run(self, dist_dir: Directory) -> StepResult:
        dist_tar: File
        try:
            dir_files = await dist_dir.entries()
            tar_files = [f for f in dir_files if f.endswith(".tar")]
            num_files = len(tar_files)
            if num_files != 1:
                error_message = (
                    "The distribution tar file for the current java connector was not built."
                    if num_files == 0
                    else "More than one distribution tar file was built for the current java connector."
                )
                return StepResult(step=self, status=StepStatus.FAILURE, stderr=error_message)
            dist_tar = dist_dir.file(tar_files[0])
        except QueryError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))
        return await super()._run(dist_tar)

    async def _build_connector(self, platform: Platform, dist_tar: File) -> Container:
        return await java.with_airbyte_java_connector(self.context, dist_tar, platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    """Create the java connector distribution tar file and build the connector image."""

    if context.use_host_gradle_dist_tar and context.is_local:
        # Special case: use a local dist tar to speed up local development.
        dist_dir = await context.dagger_client.host().directory(dist_tar_directory_path(context), include=["*.tar"])
        # Speed things up by only building for the local platform.
        return await BuildConnectorImages(context).run(dist_dir)

    # Default case: distribution tar is built by the dagger pipeline.
    build_connector_tar_result = await BuildConnectorDistributionTar(context).run()
    if build_connector_tar_result.status is not StepStatus.SUCCESS:
        return build_connector_tar_result

    dist_dir = await build_connector_tar_result.output.directory("build/distributions")
    return await BuildConnectorImages(context).run(dist_dir)


def dist_tar_directory_path(context: ConnectorContext) -> str:
    return f"{context.connector.code_directory}/build/distributions"
