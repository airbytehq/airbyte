#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pipelines.bases import StepResult
from pipelines.gradle import GradleTask
from pipelines.utils import get_exec_result


class FormatConnectorCode(GradleTask):
    """
    A step to format a Java connector code.
    """

    title = "Format connector code"

    async def _run(self) -> StepResult:
        formatted = (
            self.with_gradle(sources_to_include=self.build_include)
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            .with_exec(["./gradlew", "format"])
        )
        exit_code, stdout, stderr = await get_exec_result(formatted)
        return StepResult(
            self,
            self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output_artifact=formatted.directory(str(self.context.connector.code_directory)),
        )
