#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncer
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.utils import with_exit_code, with_stderr, with_stdout


class FormatConnectorCode(Step):
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

    async def _run(self) -> StepResult:
        formatted = (
            environments.with_testing_dependencies(self.context)
            .with_mounted_directory("/connector_code", self.context.get_connector_dir())
            .with_workdir("/connector_code")
            .with_exec(self.licenseheaders_cmd)
            .with_exec(self.isort_cmd)
            .with_exec(self.black_cmd)
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
            output_artifact=formatted.directory("/connector_code"),
        )
