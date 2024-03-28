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


class SetJavaCDKVersion(Step):
    context: ConnectorContext
    title = "Set Java CDK Version"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
    ) -> None:
        super().__init__(context)
        self.new_version = new_version

    async def _run(self) -> StepResult:
        context = self.context

        target_java_cdk_version = target_java_cdk_version
        if target_java_cdk_version == "":
            cdk_version_properties = context.get_repo_file("/airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties")
            version_properties_content = cdk_version_properties.contents()
            target_java_cdk_version = re.search(r"version *= *(?P<version>[0-9]*\.[0-9]*\.[0-9]*)", og_build_gradle_content).group(
                "version"
            )

        og_connector_dir = await context.get_connector_dir()
        if "build.gradle" not in await og_connector_dir.entries():
            return self.skip("Connector does not have a build.gradle file.")
        build_gradle = og_connector_dir.file("build.gradle")
        build_gradle_content = await build_gradle.contents()
        try:
            airbyte_java_cdk_dependency = re.search(r"cdkVersionRequired *= *'[0-9]*\.[0-9]*\.[0-9]*'", build_gradle_content)
            # If there is no airbyte-cdk dependency, add the version
            if airbyte_java_cdk_dependency is not None:
                new_version = f"cdkVersionRequired = '{self.new_version}'"
                return og_build_gradle_content.replace(airbyte_java_cdk_dependency.group(), new_version)
            else:
                raise ValueError("Could not find airbyte-cdk dependency in build.gradle")

            updated_connector_dir = og_connector_dir.with_new_file("build.gradle", updated_build_gradle_content)
            diff = og_connector_dir.diff(updated_connector_dir)
            exported_successfully = await diff.export(os.path.join(git.get_git_repo_path(), context.connector.code_directory))
            if not exported_successfully:
                return StepResult(
                    self,
                    StepStatus.FAILURE,
                    stdout="Could not export diff to local git repo.",
                )
            return StepResult(self, StepStatus.SUCCESS, stdout=f"Updated Java CDK version to {self.new_version}", output_artifact=diff)
        except ValueError as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr=f"Could not set Java CDK version: {e}",
                exc_info=e,
            )


async def run_connector_java_cdk_upgrade_pipeline(
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
            set_java_cdk_version = SetJavaCDKVersion(
                context,
                target_version,
            )
            set_java_cdk_version_result = await set_java_cdk_version.run()
            steps_results.append(set_java_cdk_version_result)
            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION JAVA CDK UPGRADE RESULTS")
            context.report = report
    return report
