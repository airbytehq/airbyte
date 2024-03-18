#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

from connector_ops.utils import ConnectorLanguage  # type: ignore
from dagger import Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.helpers import git
from pipelines.helpers.connectors import cdk_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Optional

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

        try:
            og_connector_dir = await context.get_connector_dir()
            if self.context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                updated_connector_dir = await self.upgrade_cdk_version_for_python_connector(og_connector_dir)
            elif self.context.connector.language is ConnectorLanguage.JAVA:
                updated_connector_dir = await self.upgrade_cdk_version_for_java_connector(og_connector_dir)
            else:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"No CDK for connector {self.context.connector.technical_name} of written in {self.context.connector.language}",
                )

            if updated_connector_dir is None:
                return self.skip(self.skip_reason)
            diff = og_connector_dir.diff(updated_connector_dir)
            exported_successfully = await diff.export(os.path.join(git.get_git_repo_path(), context.connector.code_directory))
            if not exported_successfully:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stdout="Could not export diff to local git repo.",
                )
            return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"Updated CDK version to {self.new_version}", output=diff)
        except ValueError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=f"Could not set CDK version: {e}",
                exc_info=e,
            )

    async def upgrade_cdk_version_for_java_connector(self, og_connector_dir: Directory) -> Directory:
        if "build.gradle" not in await og_connector_dir.entries():
            raise ValueError(f"Java connector {self.context.connector.technical_name} does not have a build.gradle file.")

        build_gradle = og_connector_dir.file("build.gradle")
        build_gradle_content = await build_gradle.contents()

        old_cdk_version_required = re.search(r"cdkVersionRequired *= *'(?P<version>[0-9]*\.[0-9]*\.[0-9]*)?'", build_gradle_content)
        # If there is no airbyte-cdk dependency, add the version
        if old_cdk_version_required is None:
            raise ValueError("Could not find airbyte-cdk dependency in build.gradle")

        if self.new_version == "latest":
            new_version = await cdk_helpers.get_latest_java_cdk_version(self.context.get_repo_dir())
        else:
            new_version = self.new_version

        updated_build_gradle = build_gradle_content.replace(old_cdk_version_required.group("version"), new_version)

        use_local_cdk = re.search(r"useLocalCdk *=.*", updated_build_gradle)
        if use_local_cdk is not None:
            updated_build_gradle = updated_build_gradle.replace(use_local_cdk.group(), "useLocalCdk = false")

        return og_connector_dir.with_new_file("build.gradle", updated_build_gradle)

    async def upgrade_cdk_version_for_python_connector(self, og_connector_dir: Directory) -> Optional[Directory]:
        context = self.context
        og_connector_dir = await context.get_connector_dir()
        if "setup.py" not in await og_connector_dir.entries():
            self.skip_reason = f"Python connector {self.context.connector.technical_name} does not have a setup.py file."
            return None
        setup_py = og_connector_dir.file("setup.py")
        setup_py_content = await setup_py.contents()

        airbyte_cdk_dependency = re.search(
            r"airbyte-cdk(?P<extra>\[[a-zA-Z0-9-]*\])?(?P<version>[<>=!~]+[0-9]*(?:\.[0-9]*)?(?:\.[0-9]*)?)?", setup_py_content
        )
        # If there is no airbyte-cdk dependency, add the version
        if airbyte_cdk_dependency is None:
            raise ValueError("Could not find airbyte-cdk dependency in setup.py")

        if self.new_version == "latest":
            new_version = cdk_helpers.get_latest_python_cdk_version()
        else:
            new_version = self.new_version

        new_version_str = f"airbyte-cdk{airbyte_cdk_dependency.group('extra') or ''}>={new_version}"
        updated_setup_py = setup_py_content.replace(airbyte_cdk_dependency.group(), new_version_str)

        return og_connector_dir.with_new_file("setup.py", updated_setup_py)


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
