#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
import re
from typing import TYPE_CHECKING

import semver
import yaml  # type: ignore
from dagger import Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers import git
from pipelines.helpers.changelog import Changelog
from pipelines.helpers.connectors.dagger_fs import dagger_export_file, dagger_file_exists, dagger_read_file, dagger_write_file
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


def get_bumped_version(version: str | None, bump_type: str) -> str:
    if version is None:
        raise ValueError("Version is not set")
    current_version = semver.VersionInfo.parse(version)
    if bump_type == "patch":
        new_version = current_version.bump_patch()
    elif bump_type == "minor":
        new_version = current_version.bump_minor()
    elif bump_type == "major":
        new_version = current_version.bump_major()
    else:
        raise ValueError(f"Unknown bump type: {bump_type}")
    return str(new_version)


class RestoreVersionState(Step):
    context: ConnectorContext

    title = "Restore original version state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        connector = context.connector
        if connector.metadata_file_path.is_file():
            self.metadata_content = connector.metadata_file_path.read_text()
        else:
            self.metadata_content = None

        if connector.dockerfile_file_path.is_file():
            self.dockerfile_content = connector.dockerfile_file_path.read_text()
        else:
            self.dockerfile_content = None

        if connector.pyproject_file_path.is_file():
            self.poetry_content = connector.pyproject_file_path.read_text()
        else:
            self.poetry_content = None

        if connector.documentation_file_path and connector.documentation_file_path.is_file():
            self.documentation_content = connector.documentation_file_path.read_text()
        else:
            self.documentation_content = None

    async def _run(self) -> StepResult:
        connector = self.context.connector
        if self.metadata_content:
            connector.metadata_file_path.write_text(self.metadata_content)
        if self.dockerfile_content:
            connector.dockerfile_file_path.write_text(self.dockerfile_content)
        if self.poetry_content:
            connector.pyproject_file_path.write_text(self.poetry_content)
        if self.documentation_content and connector.documentation_file_path:
            connector.documentation_file_path.write_text(self.documentation_content)
        return StepResult(step=self, status=StepStatus.SUCCESS)

    async def _cleanup(self) -> StepResult:
        return StepResult(step=self, status=StepStatus.SUCCESS)


class AddChangelogEntry(Step):
    context: ConnectorContext
    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
        comment: str,
        pull_request_number: str,
        repo_dir: Directory | None = None,
        export: bool = True,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = semver.VersionInfo.parse(new_version)
        self.comment = comment
        self.pull_request_number = int(pull_request_number)
        self.export = export

    async def _run(self, pull_request_number: int | None = None) -> StepResult:
        if self.repo_dir is None:
            self.repo_dir = await self.context.get_repo_dir(include=[str(self.context.connector.local_connector_documentation_directory)])

        if pull_request_number is None:
            # this allows passing it dynamically from a result of another action (like creating a pull request)
            pull_request_number = self.pull_request_number

        doc_path = self.context.connector.documentation_file_path
        if not doc_path or not doc_path.exists():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output=self.repo_dir,
            )
        try:
            original_markdown = doc_path.read_text()
            changelog = Changelog(original_markdown)
            changelog.add_entry(self.new_version, datetime.date.today(), pull_request_number, self.comment)
            updated_doc = changelog.to_markdown()
        except Exception as e:
            return StepResult(
                step=self, status=StepStatus.FAILURE, stderr=f"Could not add changelog entry: {e}", output=self.repo_dir, exc_info=e
            )
        self.repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        if self.export:
            await self.repo_dir.file(str(doc_path)).export(str(doc_path))
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output=self.repo_dir,
        )


class SetConnectorVersion(Step):
    context: ConnectorContext
    title = "Upgrade the version of the connector"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
        repo_dir: Directory | None = None,
        export: bool = True,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version
        self.export = export

    async def get_repo_dir(self) -> Directory:
        if self.repo_dir is None:
            self.repo_dir = await self.context.get_repo_dir()
        return self.repo_dir

    async def _run(self) -> StepResult:
        result = await self.update_metadata()
        if result.status is not StepStatus.SUCCESS:
            return result

        # Update the version of the connector in the Dockerfile.
        # TODO: This can be removed once we ditch all Dockerfiles from connectors.
        if self.context.connector.dockerfile_file_path.is_file():
            result = await self.update_dockerfile()
            if result.status is not StepStatus.SUCCESS:
                return result

        if self.context.connector.pyproject_file_path.is_file():
            result = await self.update_package_version()
            if result.status is not StepStatus.SUCCESS:
                return result

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated connector to {self.new_version}",
            output=self.repo_dir,
        )

    async def update_metadata(self) -> StepResult:
        repo_dir = await self.get_repo_dir()
        file_path = self.context.connector.metadata_file_path
        if not await dagger_file_exists(repo_dir, file_path):
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="Connector does not have a metadata file.", output=self.repo_dir)

        content = await dagger_read_file(repo_dir, file_path)
        metadata = yaml.safe_load(content)
        current_version = metadata.get("data", {}).get("dockerImageTag")

        if current_version is None:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Can't retrieve the connector current version.",
                output=self.repo_dir,
            )

        new_content = content.replace("dockerImageTag: " + current_version, "dockerImageTag: " + self.new_version)
        self.repo_dir = dagger_write_file(repo_dir, file_path, new_content)

        metadata_validation_results = await MetadataValidation(self.context).run()
        # Exit early if the metadata file is invalid.
        if metadata_validation_results.status is not StepStatus.SUCCESS:
            return metadata_validation_results

        if self.export:
            await dagger_export_file(self.repo_dir, file_path)

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {current_version} to {self.new_version} in {file_path}",
            output=self.repo_dir,
        )

    async def update_dockerfile(self) -> StepResult:
        repo_dir = await self.get_repo_dir()
        file_path = self.context.connector.dockerfile_file_path
        if not await dagger_file_exists(repo_dir, file_path):
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout=f"Connector does not have a Dockerfile. Tried: {file_path}",
                output=self.repo_dir,
            )

        content = await dagger_read_file(repo_dir, file_path)
        new_content = re.sub(r"(?<=\bio.airbyte.version=)(.*)", self.new_version, content)
        self.repo_dir = dagger_write_file(repo_dir, file_path, new_content)

        if self.export:
            assert self.repo_dir is not None
            await dagger_export_file(self.repo_dir, file_path)

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated Dockerfile to {self.new_version} in {file_path}",
            output=self.repo_dir,
        )

    async def update_package_version(self) -> StepResult:
        repo_dir = await self.get_repo_dir()
        file_path = self.context.connector.pyproject_file_path
        if not await dagger_file_exists(repo_dir, file_path):
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout=f"Connector does not have a Dockerfile. Tried: {file_path}",
                output=self.repo_dir,
            )

        content = await dagger_read_file(repo_dir, file_path)
        new_content = re.sub(r"(?<=^version = \")(.*)(?=\")", self.new_version, content)
        self.repo_dir = await dagger_write_file(repo_dir, file_path, new_content)

        if self.export:
            assert self.repo_dir is not None
            await dagger_export_file(self.repo_dir, file_path)

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated the package version to {self.new_version} in {file_path}",
            output=self.repo_dir,
        )


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    bump_type: str,
    changelog_entry: str,
    pull_request_number: str,
) -> Report:
    """Run a pipeline to upgrade for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        Report: The reports holding the base image version upgrade results.
    """
    async with semaphore:
        steps_results = []
        async with context:
            og_repo_dir = await context.get_repo_dir()
            new_version = get_bumped_version(context.connector.version, bump_type)
            update_docker_image_tag_in_metadata = SetConnectorVersion(context, new_version, og_repo_dir, False)
            update_docker_image_tag_in_metadata_result = await update_docker_image_tag_in_metadata.run()
            repo_dir_with_updated_metadata = update_docker_image_tag_in_metadata_result.output
            steps_results.append(update_docker_image_tag_in_metadata_result)

            add_changelog_entry = AddChangelogEntry(
                context,
                new_version,
                changelog_entry,
                pull_request_number,
                repo_dir_with_updated_metadata,
                False,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)

            final_repo_dir = add_changelog_entry_result.output
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))

            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
            context.report = report
    return report
