#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pipelines.actions import environments
from pipelines.bases import StepResult, StepStatus
from pipelines.contexts import CDKContext
from pipelines.gradle import GradleTask


class BuildCDKArtifact(GradleTask):
    DEFAULT_TASKS_TO_EXCLUDE = []
    title = "Build CDK artifact"
    gradle_task_name = "assemble"

    async def _run(self) -> StepResult:
        # TODO: use non hardcoded path
        cdk_path = str("./airbyte-cdk/java")


        with_built_container = (
            environments.with_gradle(
                self.context,
                self.build_include,
                False
            )
            .with_mounted_directory(cdk_path, self.context.dagger_client.host().directory(cdk_path))
            .with_exec(["ls", "-lah"])
            .with_exec(["pwd"])
            .with_exec(self._get_gradle_command())
            .with_workdir(f"{self.context.cdk.code_directory}/build/distributions")
        )
        await with_built_container.sync()
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout="The artifact for the cdk was successfully built.",
            output_artifact=with_built_container
        )
    

async def run_cdk_build(context: CDKContext) -> StepResult:
    """Create the java connector distribution tar file and build the connector image."""

    build_connector_tar_result = await BuildCDKArtifact(context).run()

    return build_connector_tar_result
