#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Tuple

from pipelines.actions import environments
from pipelines.bases import StepResult
from pipelines.connector_changes.common import ConnectorChangeStep


class FormatConnectorCode(ConnectorChangeStep):
    """
    A step to format a Python connector code.
    """

    title = "Format connector code"

    @property
    def black_cmd(self):
        return ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    @property
    def isort_cmd(self):
        return ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    @property
    def licenseheaders_cmd(self):
        return [
            "python",
            "-m",
            "licenseheaders",
            f"--tmpl=/{environments.LICENSE_SHORT_FILE_PATH}",
            "--ext=py",
            "--exclude=**/models/__init__.py",
        ]

    async def make_connector_change(self) -> Tuple[StepResult, List[str]]:
        in_container_code_dir = f"/airbyte/{self.context.connector.code_directory}"

        formatted = (
            environments.with_testing_dependencies(self.context)
            .with_mounted_directory(in_container_code_dir, await (await self.get_connector_dir()))
            .with_workdir(in_container_code_dir)
            .with_exec(self.licenseheaders_cmd)
            .with_exec(self.isort_cmd)
            .with_exec(self.black_cmd)
        )
        format_result = await self.get_step_result(formatted)
        self.container_with_airbyte_repo = self.container_with_airbyte_repo.with_directory(
            in_container_code_dir, format_result.output_artifact.directory(in_container_code_dir)
        )
        return StepResult(
            self,
            status=format_result.status,
            stdout=format_result.stdout,
            stderr=format_result.stderr,
            output_artifact=self.container_with_airbyte_repo,
        )
