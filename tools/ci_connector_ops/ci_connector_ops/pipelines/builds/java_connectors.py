#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import StepResult, StepStatus
from ci_connector_ops.pipelines.builds.common import BuildConnectorImageBase, BuildConnectorImageForAllPlatformsBase
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.gradle import GradleTask
from ci_connector_ops.pipelines.utils import with_exit_code
from dagger import File, QueryError


class BuildConnectorDistributionTar(GradleTask):

    title = "Build connector tar"
    gradle_task_name = "distTar"

    async def _run(self) -> StepResult:
        with_built_tar = (
            environments.with_gradle(
                self.context,
                self.build_include,
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            .with_exec(self._get_gradle_command())
            .with_workdir(f"{self.context.connector.code_directory}/build/distributions")
        )
        distributions = await with_built_tar.directory(".").entries()
        tar_files = [f for f in distributions if f.endswith(".tar")]
        await self._export_gradle_dependency_cache(with_built_tar)
        if len(tar_files) == 1:
            return StepResult(
                self,
                StepStatus.SUCCESS,
                stdout="The tar file for the current connector was successfully built.",
                output_artifact=with_built_tar.file(tar_files[0]),
            )
        else:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr="The distributions directory contains multiple connector tar files. We can't infer which one should be used. Please review and delete any unnecessary tar files.",
            )


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    async def _run(self, distribution_tar: File) -> StepResult:
        try:
            java_connector = await environments.with_airbyte_java_connector(self.context, distribution_tar, self.build_platform)
            spec_exit_code = await with_exit_code(java_connector.with_exec(["spec"]))
            if spec_exit_code != 0:
                return StepResult(
                    self, StepStatus.FAILURE, stderr=f"Failed to run spec on the connector built for platform {self.build_platform}."
                )
            return StepResult(
                self, StepStatus.SUCCESS, stdout="The connector image was successfully built.", output_artifact=java_connector
            )
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))


class BuildConnectorImageForAllPlatforms(BuildConnectorImageForAllPlatformsBase):
    """Build a Java connector image for all platforms."""

    async def _run(self, distribution_tar: File) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_connector_step_result = await BuildConnectorImage(self.context, platform).run(distribution_tar)
            if build_connector_step_result.status is not StepStatus.SUCCESS:
                return build_connector_step_result
            build_results_per_platform[platform] = build_connector_step_result.output_artifact
        return self.get_success_result(build_results_per_platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    """Create the java connector distribution tar file and build the connector image."""

    build_connector_tar_result = await BuildConnectorDistributionTar(context).run()
    if build_connector_tar_result.status is not StepStatus.SUCCESS:
        return build_connector_tar_result

    return await BuildConnectorImageForAllPlatforms(context).run(build_connector_tar_result.output_artifact)
