#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Tuple

import asyncer
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.format.common import ExportChanges
from ci_connector_ops.pipelines.git import GitPushChanges
from ci_connector_ops.pipelines.gradle import GradleTask
from ci_connector_ops.pipelines.utils import with_exit_code, with_stderr, with_stdout


class FormatConnectorCode(GradleTask):
    """
    A step to format a Java connector code.
    """

    title = "Format connector code"

    def _get_gradle_command(self, extra_options: Tuple[str] = ...) -> List:
        return ["./gradlew", "format"]

    async def _run(self) -> StepResult:
        formatted = (
            environments.with_gradle(self.context, self.build_include, bind_to_docker_host=self.BIND_TO_DOCKER_HOST)
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            .with_exec(self._get_gradle_command())
        )
        async with asyncer.create_task_group() as task_group:
            soon_exit_code = task_group.soonify(with_exit_code)(formatted)
            soon_stderr = task_group.soonify(with_stderr)(formatted)
            soon_stdout = task_group.soonify(with_stdout)(formatted)

        return StepResult(
            self,
            StepStatus.from_exit_code(soon_exit_code.value),
            stderr=soon_stderr.value,
            stdout=soon_stdout.value,
            output_artifact=formatted.directory(str(self.context.connector.code_directory)),
        )


async def run_connector_format(context: ConnectorContext) -> List[StepResult]:
    steps_results = []
    format_connector_code_result = await FormatConnectorCode(context).run()
    steps_results.append(format_connector_code_result)

    if context.is_local:
        export_changes_results = await ExportChanges(context).run(
            format_connector_code_result.output_artifact, str(context.connector.code_directory)
        )
        steps_results.append(export_changes_results)
    else:
        git_push_changes_results = await GitPushChanges(context).run(
            format_connector_code_result.output_artifact,
            str(context.connector.code_directory),
            f"Auto format {context.connector.technical_name} code",
        )
        steps_results.append(git_push_changes_results)
    return steps_results
