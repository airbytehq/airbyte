#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import StepResult, StepStatus
from ci_connector_ops.pipelines.gradle import GradleTask
from ci_connector_ops.pipelines.utils import get_exec_result


class FormatConnectorCode(GradleTask):
    """
    A step to format a Java connector code.
    """

    title = "Format connector code"

    async def _run(self) -> StepResult:
        formatted = (
            environments.with_gradle(self.context, self.build_include, bind_to_docker_host=self.BIND_TO_DOCKER_HOST)
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            .with_exec(["./gradlew", "format"])
        )
        exit_code, stdout, stderr = await get_exec_result(formatted)
        return StepResult(
            self,
            StepStatus.from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output_artifact=formatted.directory(str(self.context.connector.code_directory)),
        )
