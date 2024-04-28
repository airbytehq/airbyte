#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
import re
from typing import TYPE_CHECKING

import semver
from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers import git
from pipelines.helpers.changelog import Changelog
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


def get_bumped_version(version: str | None, bump_type: str) -> str:
    if version is None:
        raise Exception("Version is not set")
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


class AddChangelogEntry(Step):
    context: ConnectorContext
    title = "Add changelog entry"  # type: ignore

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        new_version: str,
        comment: str,
        pull_request_number: str,
        export_docs: bool = False,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = semver.VersionInfo.parse(new_version)
        self.comment = comment
        self.pull_request_number = int(pull_request_number)
        self.export_docs = export_docs

    async def _run(self, pull_request_number: int | None = None) -> StepResult:  # type: ignore
        if pull_request_number is None:
            # this allows passing it dyanmically from a result of another action (like creating a pull request)
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
        updated_repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        if self.export_docs:
            await updated_repo_dir.file(str(doc_path)).export(str(doc_path))
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output=updated_repo_dir,
        )


class SetConnectorVersion(Step):
    context: ConnectorContext
    title = "Upgrade the version of the connector"  # type: ignore

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

    @staticmethod
    def get_metadata_with_bumped_version(previous_version: str, new_version: str, metadata_str: str) -> str:
        return metadata_str.replace("dockerImageTag: " + previous_version, "dockerImageTag: " + new_version)

    async def get_repo_dir(self) -> Directory:
        if not self.repo_dir:
            self.repo_dir = await self.context.get_repo_dir(include=[str(self.context.connector.code_directory)])
        return self.repo_dir

    async def _run(self) -> StepResult:  # type: ignore
        result = await self.update_metadata()
        if result.status is not StepStatus.SUCCESS:
            return result

        if self.context.connector.dockerfile_file_path.is_file():
            result = await self.update_dockerfile()
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
        metadata_path = self.context.connector.metadata_file_path
        current_metadata = await metadata_change_helpers.get_current_metadata(repo_dir, metadata_path)
        current_metadata_str = await metadata_change_helpers.get_current_metadata_str(repo_dir, metadata_path)
        current_version = metadata_change_helpers.get_current_version(current_metadata)
        if current_version is None:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Can't retrieve the connector current version.",
                output=self.repo_dir,
            )
        updated_metadata_str = self.get_metadata_with_bumped_version(current_version, self.new_version, current_metadata_str)
        self.repo_dir = metadata_change_helpers.get_repo_dir_with_updated_metadata_str(repo_dir, metadata_path, updated_metadata_str)
        metadata_validation_results = await MetadataValidation(self.context).run()
        # Exit early if the metadata file is invalid.
        if metadata_validation_results.status is not StepStatus.SUCCESS:
            return metadata_validation_results

        if self.export:
            await self.repo_dir.file(str(metadata_path)).export(str(metadata_path))

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {current_version} to {self.new_version} in {metadata_path}",
            output=self.repo_dir,
        )

    async def update_dockerfile(self) -> StepResult:
        repo_dir = await self.get_repo_dir()
        file_path = self.context.connector.dockerfile_file_path
        if not file_path.exists():
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="Connector does not have a Dockerfile.", output=self.repo_dir)

        content = await repo_dir.file(str(file_path)).contents()
        new_content = re.sub(r"(?<=\bio.airbyte.version=)(.*)", self.new_version, content)
        self.repo_dir = repo_dir.with_new_file(str(file_path), contents=new_content)

        if self.export:
            await self.repo_dir.file(str(file_path)).export(str(file_path))

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated Dockerfile to {self.new_version} in {file_path}",
            output=self.repo_dir,
        )


# TODO: this doesn't bump the pyproject.toml file (or setup.py?) which is also needed for the version bump
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
                repo_dir_with_updated_metadata,
                new_version,
                changelog_entry,
                pull_request_number,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)

            final_repo_dir = add_changelog_entry_result.output
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))

            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
            context.report = report
    return report  # type: ignore
