#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from dagger import Directory


class ExportChanges(Step):

    title = "Export changes to local repository"

    async def _run(self, changed_directory: Directory, changed_directory_path_in_repo: str) -> StepResult:
        await changed_directory.export(changed_directory_path_in_repo)
        return StepResult(self, StepStatus.SUCCESS, stdout=f"Changes exported to {changed_directory_path_in_repo}")
