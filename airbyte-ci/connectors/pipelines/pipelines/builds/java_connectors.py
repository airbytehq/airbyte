#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from dagger import Container, Directory, ExecError, File, QueryError
from pipelines.actions import environments
from pipelines.bases import StepResult, StepStatus
from pipelines.builds.common import BuildConnectorImageBase, BuildConnectorImageForAllPlatformsBase
from pipelines.contexts import ConnectorContext
from pipelines.gradle import GradleTask


class BuildConnectorDistributionTar(GradleTask):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    title = "Build connector tar"
    gradle_task_name = "distTar"


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    async def _run(self, dist_dir: Directory) -> StepResult:
        dist_tar, error_message = await extract_tar_from_dir(dist_dir)
        if error_message is not None:
            return StepResult(self, StepStatus.FAILURE, stderr=error_message)

        try:
            java_connector = await environments.with_airbyte_java_connector(self.context, dist_tar, self.build_platform)
            try:
                await java_connector.with_exec(["spec"])
            except ExecError:
                return StepResult(
                    self, StepStatus.FAILURE, stderr=f"Failed to run spec on the connector built for platform {self.build_platform}."
                )
            return StepResult(
                self, StepStatus.SUCCESS, stdout="The connector image was successfully built.", output_artifact=java_connector
            )
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))


async def extract_tar_from_dir(dist_dir: Directory):
    """Extract single tar file from gradle distTar output directory."""
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
            return None, error_message

        return dist_dir.file(tar_files[0]), None
    except QueryError as e:
        return None, str(e)


class BuildConnectorImageForAllPlatforms(BuildConnectorImageForAllPlatformsBase):
    """Build a Java connector image for all platforms."""

    async def _run(self, dist_dir: Directory) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_connector_step_result = await BuildConnectorImage(self.context, platform).run(dist_dir)
            if build_connector_step_result.status is not StepStatus.SUCCESS:
                return build_connector_step_result
            build_results_per_platform[platform] = build_connector_step_result.output_artifact
        return self.get_success_result(build_results_per_platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    """Create the java connector distribution tar file and build the connector image."""
    dist_dir: Directory

    if context.use_host_gradle_dist_tar:
        # Special case: use a local dist tar to speed up local development.
        host_path = f"{context.connector.code_directory}/build/distributions"
        dist_dir = context.dagger_client.host().directory(host_path, include=["*.tar"])

    else:
        # Default case: distribution tar is built by the dagger pipeline.
        build_connector_tar_result = await BuildConnectorDistributionTar(context).run()
        if build_connector_tar_result.status is not StepStatus.SUCCESS:
            return build_connector_tar_result
        dist_tar_container = build_connector_tar_result.output_artifact
        dist_dir = dist_tar_container.directory(f"{context.connector.code_directory}/build/distributions")

    return await BuildConnectorImageForAllPlatforms(context).run(dist_dir)
