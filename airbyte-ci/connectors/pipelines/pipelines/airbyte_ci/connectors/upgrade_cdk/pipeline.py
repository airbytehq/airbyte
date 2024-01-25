#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.helpers import git
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


class SetCDKVersion(Step):
    context: ConnectorContext
    title = "Set CDK Version"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
    ) -> None:
        super().__init__(context)
        self.new_version = new_version

    async def _run(self) -> StepResult:
        context = self.context
        og_connector_dir = await context.get_connector_dir()
        if "setup.py" not in await og_connector_dir.entries():
            return self.skip("Connector does not have a setup.py file.")
        setup_py = og_connector_dir.file("setup.py")
        setup_py_content = await setup_py.contents()
        try:
            updated_setup_py = self.update_cdk_version(setup_py_content)
            updated_connector_dir = og_connector_dir.with_new_file("setup.py", updated_setup_py)
            diff = og_connector_dir.diff(updated_connector_dir)
            exported_successfully = await diff.export(os.path.join(git.get_git_repo_path(), context.connector.code_directory))
            if not exported_successfully:
                return StepResult(
                    self,
                    StepStatus.FAILURE,
                    stdout="Could not export diff to local git repo.",
                )
            return StepResult(self, StepStatus.SUCCESS, stdout=f"Updated CDK version to {self.new_version}", output_artifact=diff)
        except ValueError as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr=f"Could not set CDK version: {e}",
                exc_info=e,
            )

    def update_cdk_version(self, og_setup_py_content: str) -> str:
        airbyte_cdk_dependency = re.search(
            r"airbyte-cdk(?P<extra>\[[a-zA-Z0-9-]*\])?(?P<version>[<>=!~]+[0-9]*\.[0-9]*\.[0-9]*)?", og_setup_py_content
        )
        # If there is no airbyte-cdk dependency, add the version
        if airbyte_cdk_dependency is not None:
            new_version = f"airbyte-cdk{airbyte_cdk_dependency.group('extra') or ''}>={self.new_version}"
            return og_setup_py_content.replace(airbyte_cdk_dependency.group(), new_version)
        else:
            raise ValueError("Could not find airbyte-cdk dependency in setup.py")


async def run_connector_cdk_upgrade_pipeline(
    context: ConnectorContext,
    semaphore: Semaphore,
    target_version: str,
) -> Report:
    """Run a pipeline to upgrade the CDK version for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        Report: The reports holding the CDK version set results.
    """
    async with semaphore:
        steps_results = []
        async with context:
            set_cdk_version = SetCDKVersion(
                context,
                target_version,
            )
            set_cdk_version_result = await set_cdk_version.run()
            steps_results.append(set_cdk_version_result)
            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION CDK UPGRADE RESULTS")
            context.report = report
    return report
