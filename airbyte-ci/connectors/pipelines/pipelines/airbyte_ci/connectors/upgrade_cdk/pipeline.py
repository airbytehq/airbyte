#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

import toml
from connector_ops.utils import ConnectorLanguage  # type: ignore
from dagger import Directory

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers import git
from pipelines.helpers.connectors import cdk_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Optional

    from anyio import Semaphore

# GLOBALS

POETRY_LOCK_FILENAME = "poetry.lock"
PYPROJECT_FILENAME = "pyproject.toml"


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
                    status=StepStatus.SKIPPED,
                    stdout=f"The upgrade-cdk command does not support {self.context.connector.language} connectors.",
                )

            if updated_connector_dir is None:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"No changes were made to the CDK version for connector {self.context.connector.technical_name}",
                )
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

        # Check for existing pyproject file and load contents
        pyproject_toml = og_connector_dir.file(PYPROJECT_FILENAME)
        if not pyproject_toml:
            raise ValueError(f"Could not find 'pyproject.toml' for {context.connector.technical_name}")
        pyproject_content = await pyproject_toml.contents()
        pyproject_data = toml.loads(pyproject_content)

        # Grab the airbyte-cdk dependency from pyproject
        dependencies = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        airbyte_cdk_dependency = dependencies.get("airbyte-cdk")
        if not airbyte_cdk_dependency:
            raise ValueError("Could not find a valid airbyte-cdk dependency in 'pyproject.toml'")

        # Set the new version. If not explicitly provided, set it to the latest version and allow non-breaking changes
        if self.new_version == "latest":
            new_version = f"^{cdk_helpers.get_latest_python_cdk_version()}"
        else:
            new_version = self.new_version
        self.logger.info(f"Setting CDK version to {new_version}")
        dependencies["airbyte-cdk"] = new_version

        updated_pyproject_toml_content = toml.dumps(pyproject_data)
        updated_connector_dir = og_connector_dir.with_new_file(PYPROJECT_FILENAME, updated_pyproject_toml_content)

        # Create a new container to run poetry lock
        base_image = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image)
        connector_container = base_container.with_mounted_directory("/connector", updated_connector_dir).with_workdir("/connector")

        poetry_lock_file = await connector_container.file(POETRY_LOCK_FILENAME).contents()
        updated_container = await connector_container.with_exec(["poetry", "lock"], use_entrypoint=True)
        updated_poetry_lock_file = await updated_container.file(POETRY_LOCK_FILENAME).contents()

        if poetry_lock_file != updated_poetry_lock_file:
            updated_connector_dir = updated_connector_dir.with_new_file(POETRY_LOCK_FILENAME, updated_poetry_lock_file)
        else:
            raise ValueError("Lockfile did not change after running poetry lock")

        return updated_connector_dir


async def run_connector_cdk_upgrade_pipeline(
    context: ConnectorContext,
    semaphore: Semaphore,
    target_version: str,
) -> ConnectorReport:
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
