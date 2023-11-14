#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from copy import deepcopy

import semver
from dagger import Container
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers import git
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus


def get_bumped_version(version: str, bump_type: str) -> str:
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
    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        new_version: str,
        changelog_entry: str,
        pull_request_number: str,
    ):
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version
        self.changelog_entry = changelog_entry
        self.pull_request_number = pull_request_number

    async def _run(self) -> StepResult:
        doc_path = self.context.connector.documentation_file_path
        if not doc_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output_artifact=self.repo_dir,
            )
        try:
            updated_doc = self.add_changelog_entry(doc_path.read_text())
        except Exception as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stdout=f"Could not add changelog entry: {e}",
                output_artifact=self.container_with_airbyte_repo,
            )
        updated_repo_dir = self.repo_dir.with_new_file(str(doc_path), updated_doc)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output_artifact=updated_repo_dir,
        )

    def find_line_index_for_new_entry(self, markdown_text) -> int:
        lines = markdown_text.splitlines()
        for line_index, line in enumerate(lines):
            if "version" in line.lower() and "date" in line.lower() and "pull request" in line.lower() and "subject" in line.lower():
                return line_index + 2
        raise Exception("Could not find the changelog section table in the documentation file.")

    def add_changelog_entry(self, og_doc_content) -> str:
        today = datetime.date.today().strftime("%Y-%m-%d")
        lines = og_doc_content.splitlines()
        line_index_for_new_entry = self.find_line_index_for_new_entry(og_doc_content)
        new_entry = f"| {self.new_version} | {today} | [{self.pull_request_number}](https://github.com/airbytehq/airbyte/pull/{self.pull_request_number}) | {self.changelog_entry} |"
        lines.insert(line_index_for_new_entry, new_entry)
        return "\n".join(lines)


class BumpDockerImageTagInMetadata(Step):
    title = "Upgrade the dockerImageTag to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        new_version: str,
    ):
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version

    @staticmethod
    def get_metadata_with_bumped_version(previous_version: str, new_version: str, current_metadata: dict) -> dict:
        updated_metadata = deepcopy(current_metadata)
        updated_metadata["data"]["dockerImageTag"] = new_version
        # Bump strict versions
        if current_metadata["data"].get("registries", {}).get("cloud", {}).get("dockerImageTag") == previous_version:
            updated_metadata["data"]["registries"]["cloud"]["dockerImageTag"] = new_version
        return updated_metadata

    async def _run(self) -> StepResult:
        metadata_path = self.context.connector.metadata_file_path
        current_metadata = await metadata_change_helpers.get_current_metadata(self.repo_dir, metadata_path)
        current_version = metadata_change_helpers.get_current_version(current_metadata)
        if current_version is None:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Can't retrieve the connector current version.",
                output_artifact=self.repo_dir,
            )
        updated_metadata = self.get_metadata_with_bumped_version(current_version, self.new_version, current_metadata)
        repo_dir_with_updated_metadata = metadata_change_helpers.get_repo_dir_with_updated_metadata(
            self.repo_dir, metadata_path, updated_metadata
        )

        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {current_version} to {self.new_version} in {metadata_path}",
            output_artifact=repo_dir_with_updated_metadata,
        )


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore,
    bump_type: str,
    changelog_entry: str,
    pull_request_number: str,
) -> ConnectorReport:
    """Run a pipeline to upgrade for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding the base image version upgrade results.
    """
    async with semaphore:
        steps_results = []
        async with context:
            og_repo_dir = await context.get_repo_dir()
            new_version = get_bumped_version(context.connector.version, bump_type)
            update_docker_image_tag_in_metadata = BumpDockerImageTagInMetadata(
                context,
                og_repo_dir,
                new_version,
            )
            update_docker_image_tag_in_metadata_result = await update_docker_image_tag_in_metadata.run()
            repo_dir_with_updated_metadata = update_docker_image_tag_in_metadata_result.output_artifact
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
            final_repo_dir = add_changelog_entry_result.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            context.report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
    return context.report
