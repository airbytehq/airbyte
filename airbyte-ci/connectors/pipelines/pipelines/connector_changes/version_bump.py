#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from typing import List, Optional

import semver
import yaml
from dagger import Container
from pipelines.bases import ConnectorReport, StepResult, StepStatus
from pipelines.connector_changes.common import ConnectorChangeStep, MetadataUpdateStep
from pipelines.contexts import ConnectorContext


class BumpDockerImageTagInMetadata(MetadataUpdateStep):
    title = "Upgrade the dockerImageTag to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
        export_changes_to_host: bool,
        container_with_airbyte_repo: Container | None = None,
        commit: bool = False,
        push: bool = False,
        skip_ci=True,
    ):
        super().__init__(context, export_changes_to_host, container_with_airbyte_repo, commit, push, skip_ci)
        self.new_version = new_version

    async def get_current_docker_image_tag(self) -> Optional[str]:
        current_metadata = await self.get_current_metadata()
        return current_metadata.get("data", {}).get("dockerImageTag")

    async def get_current_version(self) -> Optional[str]:
        return (await self.get_current_metadata()).get("data", {}).get("dockerImageTag")

    async def get_updated_metadata(self) -> str:
        current_version = await self.get_current_version()
        current_metadata = await self.get_current_metadata()
        current_metadata["data"]["dockerImageTag"] = self.new_version
        # Bump strict versions
        if current_metadata["data"].get("registries", {}).get("cloud", {}).get("dockerImageTag") == current_version:
            current_metadata["data"]["registries"]["cloud"]["dockerImageTag"] = self.new_version
        return yaml.safe_dump(current_metadata)

    async def make_connector_change(self) -> StepResult:
        og_version = await self.get_current_version()
        if og_version is None:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Can't retrieve the connector current version.",
                output_artifact=self.container_with_airbyte_repo,
            )

        container_with_updated_metadata = await self.get_container_with_updated_metadata(self.container_with_airbyte_repo)

        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {og_version} to {self.new_version} in metadata.yaml",
            output_artifact=container_with_updated_metadata,
        )


class AddChangelogEntry(ConnectorChangeStep):
    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
        changelog_entry: str,
        pull_request_number: str,
        export_changes_to_host: bool,
        container_with_airbyte_repo: Container | None = None,
        commit: bool = False,
        push: bool = False,
        skip_ci=True,
    ):
        super().__init__(context, export_changes_to_host, container_with_airbyte_repo, commit, push, skip_ci)
        self.new_version = new_version
        self.changelog_entry = changelog_entry
        self.pull_request_number = pull_request_number

    @property
    def modified_paths(self) -> List[str]:
        return [self.context.connector.documentation_file_path]

    async def make_connector_change(self) -> StepResult:
        doc_path = self.context.connector.documentation_file_path
        if not doc_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output_artifact=self.container_with_airbyte_repo,
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
        self.container_with_airbyte_repo = await self.container_with_airbyte_repo.with_new_file(str(doc_path), updated_doc)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output_artifact=self.container_with_airbyte_repo,
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


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore,
    commit_and_push: bool,
    export_changes_to_host: bool,
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
            current_version = semver.VersionInfo.parse(context.connector.version)
            if bump_type == "patch":
                new_version = current_version.bump_patch()
            elif bump_type == "minor":
                new_version = current_version.bump_minor()
            elif bump_type == "major":
                new_version = current_version.bump_major()
            new_version = str(new_version)

            update_docker_image_tag_in_metadata = BumpDockerImageTagInMetadata(
                context,
                new_version,
                export_changes_to_host,
                commit=commit_and_push,
                push=commit_and_push,
            )
            update_docker_image_tag_in_metadata_result = await update_docker_image_tag_in_metadata.run()
            steps_results.append(update_docker_image_tag_in_metadata_result)
            add_changelog_entry = AddChangelogEntry(
                context,
                new_version,
                changelog_entry,
                pull_request_number,
                export_changes_to_host,
                commit=commit_and_push,
                push=commit_and_push,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)
            context.report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
    return context.report
