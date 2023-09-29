#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import ExecError, File, QueryError
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

    async def _run(self) -> StepResult:
        result = await super()._run()
        if result.status is not StepStatus.SUCCESS:
            return result

        with_built_tar = result.output_artifact.with_workdir(f"{self.context.connector.code_directory}/build/distributions")
        distributions = await with_built_tar.directory(".").entries()
        tar_files = [f for f in distributions if f.endswith(".tar")]
        if len(tar_files) == 1:
            return StepResult(
                self,
                StepStatus.SUCCESS,
                stdout="The distribution tar file for the current java connector was built.",
                output_artifact=with_built_tar.file(tar_files[0]),
            )
        elif len(tar_files) == 0:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr="The distribution tar file for the current java connector was not built.",
            )
        else:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr="The distributions directory for this java connector contains multiple tar files. "
                "We can't infer which one should be used. "
                "Please review and delete any unnecessary tar files.",
            )


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Java connector image using the distTar Gradle task.
    """

    async def _run(self, distribution_tar: File) -> StepResult:
        try:
            java_connector = await environments.with_airbyte_java_connector(self.context, distribution_tar, self.build_platform)
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
