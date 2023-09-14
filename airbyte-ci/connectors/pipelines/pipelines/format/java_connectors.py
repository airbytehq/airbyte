#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pipelines.actions import environments
from pipelines.bases import StepResult
from pipelines.gradle import GradleTask
from pipelines.utils import get_exec_result


class FormatConnectorCode(GradleTask):
    """
    A step to format a Java connector code.
    """

    title = "Format connector code"
    gradle_task_name = "format"

    async def _run(self) -> StepResult:
        result = await super()._run()
        return StepResult(
            self,
            result.status,
            stderr=result.stderr,
            stdout=result.stdout,
            output_artifact=result.output_artifact.directory(str(self.context.connector.code_directory)),
        )
