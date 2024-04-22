#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import re
from typing import TYPE_CHECKING

import dagger
import git
import requests
import toml
from connector_ops.utils import ConnectorLanguage  # type: ignore
from jinja2 import Environment, PackageLoader, select_autoescape
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.bump_version.pipeline import AddChangelogEntry, BumpDockerImageTagInMetadata, get_bumped_version
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.python.common import with_python_connector_installed
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Iterable, List, Optional

    from anyio import Semaphore

PACKAGE_NAME_PATTERN = r"^([a-zA-Z0-9_.\-]+)(?:\[(.*?)\])?([=~><!]=?[a-zA-Z0-9\.]+)?$"


class CheckIsUpdateCdkCandidate(Step):
    """Check if the connector is a candidate for migration to poetry.
    Candidate conditions:
    - The connector is a Python connector.
    - The connector is a source connector.
    - The connector is using poetry.
    - The connector has a base image defined in the metadata.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for CDK upgrade."

    def __init__(self, context: PipelineContext, cdk_version: str) -> None:
        super().__init__(context)
        self.cdk_version = cdk_version

    async def _run(self) -> StepResult:
        connector_dir_entries = await (await self.context.get_connector_dir()).entries()
        if self.context.connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a Python connector.",
            )
        if self.context.connector.connector_type != "source":
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a source connector.",
            )
        if not "poetry.lock" in connector_dir_entries or not "pyproject.toml" in connector_dir_entries:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector requires poetry.",
            )

        if not self.context.connector.metadata or not self.context.connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector CDK can't be updated because it does not have a base image defined in the metadata.",
            )

        # TODO: is there a fast way to check if the connector is already using the latest CDK version?
        # this is better than all the docker shenanigans if it's not needed.
        # probably just grep the toml file. If can't find it fail over to the better way

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class UpdateCdk(Step):
    context: ConnectorContext

    title = "Update the CDK to a new version."

    def __init__(self, context: PipelineContext, cdk_version: str) -> None:
        super().__init__(context)
        self.cdk_version = cdk_version

    async def _run(self) -> StepResult:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image_name)
        connector_container = await with_python_connector_installed(
            self.context,
            base_container,
            str(self.context.connector.code_directory),
        )

        try:
            poetry_show_result = await connector_container.with_exec(sh_dash_c(["poetry show | grep airbyte-cdk"])).stdout()
            if not poetry_show_result:
                return StepResult(step=self, status=StepStatus.FAILURE, stderr="CDK is not installed in the connector.")
            current_cdk_version = extract_poetry_show_version(poetry_show_result)
            if not current_cdk_version:
                return StepResult(step=self, status=StepStatus.FAILURE, stderr="CDK was not found in the connector poetry.")

            self.logger.info(f"Current CDK version for {self.context.connector.technical_name}: {current_cdk_version}")

            # TODO: maybe add --force to also downgrade the CDK version
            if compare_semver_versions(current_cdk_version, self.cdk_version) >= 0:
                return StepResult(
                    step=self,
                    status=StepStatus.SKIPPED,
                    stderr=f"CDK is already up to date. Current version: {current_cdk_version}, requested version: {self.cdk_version}",
                )

            with_new_cdk = await connector_container.with_exec(["poetry", "add", f"airbyte-cdk=={self.cdk_version}"])
            await with_new_cdk.file("pyproject.toml").export(f"{self.context.connector.code_directory}/pyproject.toml")
            self.logger.info(f"Generated pyproject.toml for {self.context.connector.technical_name}")
            await with_new_cdk.file("poetry.lock").export(f"{self.context.connector.code_directory}/poetry.lock")
            self.logger.info(f"Generated poetry.lock for {self.context.connector.technical_name}")
        except dagger.ExecError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))

        return StepResult(step=self, status=StepStatus.SUCCESS)


class RestoreOriginalState(Step):
    context: ConnectorContext

    title = "Restore original state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        self.pyproject_path = context.connector.code_directory / "pyproject.toml"
        if self.pyproject_path.exists():
            self.original_pyproject = self.pyproject_path.read_text()
        self.poetry_lock_path = context.connector.code_directory / "poetry.lock"
        if self.poetry_lock_path.exists():
            self.original_poetry_lock = self.poetry_lock_path.read_text()

    async def _run(self) -> StepResult:
        if self.original_pyproject:
            self.pyproject_path.write_text(self.original_pyproject)
            self.logger.info(f"Restored pyproject.toml for {self.context.connector.technical_name}")
        if self.original_poetry_lock:
            self.poetry_lock_path.write_text(self.original_poetry_lock)
            self.logger.info(f"Restored poetry.lock for {self.context.connector.technical_name}")

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class RegressionTest(Step):
    """Run the regression test for the connector.
    We test that:
    - The original dependencies are installed in the new connector image.
    - The dev dependencies are not installed in the new connector image.
    - The connector spec command successfully.
    """

    context: ConnectorContext

    title = "Run regression test"

    async def _run(self, new_connector_container: dagger.Container) -> StepResult:
        try:
            await new_connector_container.with_exec(["spec"])
            await new_connector_container.with_mounted_file(
                "pyproject.toml", (await self.context.get_connector_dir(include=["pyproject.toml"])).file("pyproject.toml")
            ).with_exec(["poetry", "run", self.context.connector.technical_name, "spec"], skip_entrypoint=True)
        except dagger.ExecError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


def compare_semver_versions(version1: str, version2: str) -> int:
    """Compare two semver versions.
    Return:
    - 0 if the versions are equal.
    - 1 if version1 is greater than version2.
    - -1 if version1 is less than version2.
    """
    version1_parts = version1.split(".")
    version2_parts = version2.split(".")
    for i in range(3):
        if int(version1_parts[i]) > int(version2_parts[i]):
            return 1
        if int(version1_parts[i]) < int(version2_parts[i]):
            return -1
    return 0


def extract_poetry_show_version(poetry_show_result: str) -> str | None:
    # Regular expression to match a version number pattern
    version_pattern = r"\d+\.\d+\.\d+"

    # Search for the pattern in the string
    match = re.search(version_pattern, poetry_show_result)

    # Extract and print the version number if a match is found
    if match:
        return match.group()
    else:
        return None


async def get_current_cdk_version() -> str:
    response = requests.get("https://pypi.org/pypi/airbyte-cdk/json")
    response.raise_for_status()
    return response.json()["info"]["version"]


async def run_connector_up_to_date_pipeline(context: ConnectorContext, semaphore: "Semaphore", cdk_version: str | None) -> Report:
    restore_original_state = RestoreOriginalState(context)

    # TODO: could pipe in the new version from the command line
    should_bump = False
    if should_bump:
        new_version = get_bumped_version(context.connector.version, "patch")
    else:
        new_version = None

    if not cdk_version:
        cdk_version = await get_current_cdk_version()

    context.logger.info(f"CDK version: {cdk_version}")
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append(
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.CHECK_UPGRADE_CANDIDATE, step=CheckIsUpdateCdkCandidate(context, cdk_version))]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UPGRADE_CDK,
                step=UpdateCdk(context, cdk_version),
                depends_on=[CONNECTOR_TEST_STEP_ID.CHECK_UPGRADE_CANDIDATE],
            )
        ]
    )

    steps_to_run.append(
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context), depends_on=[CONNECTOR_TEST_STEP_ID.UPGRADE_CDK])]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST,
                step=RegressionTest(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
                args=lambda results: {"new_connector_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
            )
        ]
    )

    if new_version:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.BUMP_METADATA_VERSION,
                    step=BumpDockerImageTagInMetadata(
                        context,
                        await context.get_repo_dir(include=[str(context.connector.code_directory)]),
                        new_version,
                        export_metadata=True,
                    ),
                    depends_on=[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST],
                )
            ]
        )
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.ADD_CHANGELOG_ENTRY,
                    step=AddChangelogEntry(
                        context,
                        await context.get_repo_dir(include=[str(context.connector.local_connector_documentation_directory)]),
                        new_version,
                        f"Bump CDK to {cdk_version}.",
                        "0",
                        export_docs=True,
                    ),
                    depends_on=[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST],
                )
            ]
        )

    async with semaphore:
        async with context:
            try:
                result_dict = await run_steps(
                    runnables=steps_to_run,
                    options=context.run_step_options,
                )
            except Exception as e:
                await restore_original_state.run()
                raise e
            results = list(result_dict.values())
            if any(step_result.status is StepStatus.FAILURE for step_result in results):
                await restore_original_state.run()
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

    return report
