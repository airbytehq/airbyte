#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

from dagger import Container
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers import git
from pipelines.models.steps import Step, StepResult, StepStatus


class SetCDKVersion(Step):
    title = "Set CDK Version"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        new_version: str,
    ):
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version

    async def _run(self) -> StepResult:
        context: ConnectorContext = self.context
        setup_py_path = context.connector.code_directory / "setup.py"
        if not setup_py_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a setup.py file.",
                output_artifact=self.repo_dir,
            )
        try:
            updated_setup_py = self.update_cdk_version(setup_py_path.read_text())
        except Exception as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stdout=f"Could not add changelog entry: {e}",
                output_artifact=self.container_with_airbyte_repo,
            )
        updated_repo_dir = self.repo_dir.with_new_file(str(setup_py_path), updated_setup_py)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated CDK version to {self.new_version}",
            output_artifact=updated_repo_dir,
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
    semaphore,
    target_version: str,
) -> ConnectorReport:
    """Run a pipeline to upgrade the CDK version for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding the base image version upgrade results.
    """
    async with semaphore:
        steps_results = []
        async with context:
            og_repo_dir = await context.get_repo_dir()

            set_cdk_version = SetCDKVersion(
                context,
                og_repo_dir,
                target_version,
            )
            set_cdk_version_result = await set_cdk_version.run()
            steps_results.append(set_cdk_version_result)
            final_repo_dir = set_cdk_version_result.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            context.report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION CDK UPGRADE RESULTS")
    return context.report
