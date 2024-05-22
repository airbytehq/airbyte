#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

import dagger
from connector_ops.utils import ConnectorLanguage  # type: ignore
from packaging.version import Version
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.common.regression_test import RegressionTest
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.pull_request.pipeline import PULL_REQUEST_OUTPUT_ID, run_connector_pull_request_pipeline
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.python.common import with_python_connector_installed
from pipelines.helpers.connectors.cdk_helpers import get_latest_python_cdk_version
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore

POETRY_LOCK_FILE = "poetry.lock"
POETRY_TOML_FILE = "pyproject.toml"


class CheckIsPythonUpdateable(Step):
    """Check if the connector is a candidate for updates.
    Candidate conditions:
    - The connector is a Python connector.
    - The connector is a source connector.
    - The connector is using poetry.
    - The connector has a base image defined in the metadata.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for updating."

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

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
        if POETRY_LOCK_FILE not in connector_dir_entries or POETRY_TOML_FILE not in connector_dir_entries:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector requires poetry.",
            )

        if not self.context.connector.metadata or not self.context.connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector can't be updated because it does not have a base image defined in the metadata.",
            )

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class UpdatePoetry(Step):
    context: ConnectorContext
    dev: bool
    specified_versions: dict[str, str]

    title = "Update versions of libraries in poetry."

    def __init__(self, context: PipelineContext, dev: bool, specific_dependencies: List[str]) -> None:
        super().__init__(context)
        self.dev = dev
        self.specified_versions = parse_specific_dependencies(specific_dependencies)

    async def _run(self) -> StepResult:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image_name)
        connector_container = await with_python_connector_installed(
            self.context,
            base_container,
            str(self.context.connector.code_directory),
        )

        try:
            before_versions = await get_poetry_versions(connector_container)
            before_main = await get_poetry_versions(connector_container, only="main")

            if self.specified_versions:
                for package, dep in self.specified_versions.items():
                    self.logger.info(f"  Specified: poetry add {dep}")
                    if package in before_main:
                        connector_container = await connector_container.with_exec(["poetry", "add", dep])
                    else:
                        connector_container = await connector_container.with_exec(["poetry", "add", dep, "--group=dev"])
            else:
                current_cdk_version = before_versions.get("airbyte-cdk") or None
                if current_cdk_version:
                    # We want the CDK pinned exactly so it also works as expected in PyAirbyte and other `pip` scenarios
                    new_cdk_version = pick_airbyte_cdk_version(current_cdk_version, self.context)
                    self.logger.info(f"Updating airbyte-cdk from {current_cdk_version} to {new_cdk_version}")
                    if new_cdk_version > current_cdk_version:
                        connector_container = await connector_container.with_exec(["poetry", "add", f"airbyte-cdk=={new_cdk_version}"])

                # update everything else
                connector_container = await connector_container.with_exec(["poetry", "update"])
                poetry_update_output = await connector_container.stdout()
                self.logger.info(poetry_update_output)

            after_versions = await get_poetry_versions(connector_container)

            # see what changed
            all_changeset = get_package_changes(before_versions, after_versions)
            main_changeset = get_package_changes(before_main, after_versions)
            if self.specified_versions or self.dev:
                important_changeset = all_changeset
            else:
                important_changeset = main_changeset

            for package, version in main_changeset.items():
                self.logger.info(f"Main {package} updates: {before_versions.get(package) or 'None'} -> {version or 'None'}")
            for package, version in all_changeset.items():
                if package not in main_changeset:
                    self.logger.info(f" Dev {package} updates: {before_versions.get(package) or 'None'} -> {version or 'None'}")

            if not important_changeset:
                message = f"No important dependencies updated. Only {', '.join(all_changeset.keys() or ['none'])} were updated."
                self.logger.info(message)
                return StepResult(step=self, status=StepStatus.SKIPPED, stderr=message)

            await connector_container.file(POETRY_TOML_FILE).export(f"{self.context.connector.code_directory}/{POETRY_TOML_FILE}")
            self.logger.info(f"Generated {POETRY_TOML_FILE} for {self.context.connector.technical_name}")
            await connector_container.file(POETRY_LOCK_FILE).export(f"{self.context.connector.code_directory}/{POETRY_LOCK_FILE}")
            self.logger.info(f"Generated {POETRY_LOCK_FILE} for {self.context.connector.technical_name}")

        except dagger.ExecError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))

        return StepResult(step=self, status=StepStatus.SUCCESS, output=all_changeset)


class MakePullRequest(Step):
    context: ConnectorContext
    pull: bool

    title = "Bump version, add changelog, and make pull request"

    def __init__(
        self,
        context: PipelineContext,
        pull: bool,
        no_bump: bool,
        semaphore: "Semaphore",
    ) -> None:
        super().__init__(context)
        self.pull = pull
        self.no_bump = no_bump
        self.semaphore = semaphore

    async def _run(self) -> StepResult:
        message = "Updating python dependencies"  # TODO: update this based on what it actually did, used for commit and changelog
        branch_id = "up_to_date"
        title = "Up to date"
        body = "Updating python dependencies"  # TODO: update this based on what it actually did
        changelog = not self.no_bump
        if self.no_bump:
            bump = None
        else:
            bump = "patch"
        dry_run = not self.pull
        report = await run_connector_pull_request_pipeline(
            context=self.context,
            semaphore=self.semaphore,
            message=message,
            branch_id=branch_id,
            title=title,
            body=body,
            changelog=changelog,
            bump=bump,
            dry_run=dry_run,
        )

        results = report.steps_results
        pull_request_number = 0
        for step_result in results:
            if step_result.status is StepStatus.FAILURE:
                return step_result
            if hasattr(step_result.output, PULL_REQUEST_OUTPUT_ID):
                pull_request_number = step_result.output[PULL_REQUEST_OUTPUT_ID]

        return StepResult(step=self, status=StepStatus.SUCCESS, output={PULL_REQUEST_OUTPUT_ID: pull_request_number})


class RestoreUpToDateState(Step):
    context: ConnectorContext

    title = "Restore original state"

    # Note: Pull request stuff resotres itself because it's run using the outer method

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        self.pyproject_path = context.connector.code_directory / POETRY_TOML_FILE
        if self.pyproject_path.exists():
            self.original_pyproject = self.pyproject_path.read_text()
        self.poetry_lock_path = context.connector.code_directory / POETRY_LOCK_FILE
        if self.poetry_lock_path.exists():
            self.original_poetry_lock = self.poetry_lock_path.read_text()

    async def _run(self) -> StepResult:
        if self.original_pyproject:
            self.pyproject_path.write_text(self.original_pyproject)
            self.logger.info(f"Restored {POETRY_TOML_FILE} for {self.context.connector.technical_name}")
        if self.original_poetry_lock:
            self.poetry_lock_path.write_text(self.original_poetry_lock)
            self.logger.info(f"Restored {POETRY_LOCK_FILE} for {self.context.connector.technical_name}")

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


def pick_airbyte_cdk_version(current_version: Version, context: ConnectorContext) -> Version:
    latest = Version(get_latest_python_cdk_version())

    # TODO: could add more logic here for semantic and other known things

    # 0.80.0 is better beause it specifies the protocol version
    if context.connector.language == ConnectorLanguage.PYTHON and current_version < Version("0.80.0"):
        return Version("0.80.0")
    # 0.84: where from airbyte_cdk.sources.deprecated is removed
    if context.connector.language == ConnectorLanguage.PYTHON and current_version < Version("0.84.0"):
        return Version("0.83.0")

    return latest


def parse_specific_dependencies(specific_dependencies: List[str]) -> dict[str, str]:
    package_name_pattern = r"^(\w+)[@><=]([^\s]+)$"
    versions: dict[str, str] = {}
    for dep in specific_dependencies:
        match = re.match(package_name_pattern, dep)
        if match:
            package = match.group(1)
            versions[package] = dep
        else:
            raise ValueError(f"Invalid dependency name: {dep}")
    return versions


def get_package_changes(before_versions: dict[str, Version], after_versions: dict[str, Version]) -> dict[str, Version]:
    changes: dict[str, Version] = {}
    for package, before_version in before_versions.items():
        after_version = after_versions.get(package)
        if after_version and before_version != after_version:
            changes[package] = after_version
    return changes


async def get_poetry_versions(connector_container: dagger.Container, only: str | None = None) -> dict[str, Version]:
    # -T makes it only the top-level ones
    # poetry show -T --only main will jsut be the main dependecies
    command = ["poetry", "show", "-T"]
    if only:
        command.append("--only")
        command.append(only)
    poetry_show_result = await connector_container.with_exec(command).stdout()
    versions: dict[str, Version] = {}
    lines = poetry_show_result.strip().split("\n")
    for line in lines:
        parts = line.split(maxsplit=2)  # Use maxsplit to limit the split parts
        if len(parts) >= 2:
            package = parts[0]
            # Regex to find version-like patterns. saw case with (!) before version
            version_match = re.search(r"\d+\.\d+.*", parts[1])
            if version_match:
                version = version_match.group()
                versions[package] = Version(version)
    return versions


async def run_connector_up_to_date_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    dev: bool = False,
    pull: bool = False,
    no_bump: bool = False,
    specific_dependencies: List[str] = [],
) -> Report:
    restore_original_state = RestoreUpToDateState(context)

    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    do_regression_test = False

    steps_to_run: STEP_TREE = []

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.CHECK_UPDATE_CANDIDATE,
                step=CheckIsPythonUpdateable(context),
            )
        ]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UPDATE_POETRY,
                step=UpdatePoetry(context, dev, specific_dependencies),
                depends_on=[CONNECTOR_TEST_STEP_ID.CHECK_UPDATE_CANDIDATE],
            )
        ]
    )

    steps_before_pull: List[str] = [CONNECTOR_TEST_STEP_ID.UPDATE_POETRY]
    if do_regression_test:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context), depends_on=[CONNECTOR_TEST_STEP_ID.UPDATE_POETRY]
                )
            ]
        )

        steps_before_pull.append(CONNECTOR_TEST_STEP_ID.REGRESSION_TEST)
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

    if pull:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.UPDATE_PULL_REQUEST,
                    step=MakePullRequest(context, pull, no_bump, semaphore),
                    depends_on=steps_before_pull,
                )
            ]
        )

    return await run_connector_steps(context, semaphore, steps_to_run, restore_original_state=restore_original_state)
