#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import textwrap
from typing import List, Optional

import yaml
from base_images import python
from connector_ops.utils import ConnectorLanguage
from dagger import Container
from jinja2 import Template
from pipelines.bases import ConnectorReport, StepResult, StepStatus
from pipelines.connector_changes.common import ConnectorChangeStep, MetadataUpdateStep
from pipelines.connector_changes.version_bump import AddChangelogEntry, BumpDockerImageTagInMetadata, get_bumped_version
from pipelines.contexts import ConnectorContext


class UpgradeBaseImageMetadata(MetadataUpdateStep):
    title = "Upgrade the base image to the latest version in metadata.yaml"
    latest_python_version = python.VERSION_REGISTRY.latest_version.name_with_tag
    # latest_java_version = java.VERSION_REGISTRY.latest_version

    def __init__(
        self,
        context: ConnectorContext,
        export_changes_to_host: bool,
        container_with_airbyte_repo: Container | None = None,
        commit: bool = False,
        push: bool = False,
        skip_ci=True,
        set_if_not_exists: bool = False,
    ):
        super().__init__(context, export_changes_to_host, container_with_airbyte_repo, commit, push, skip_ci)
        self.set_if_not_exists = set_if_not_exists

    @property
    def latest_base_image_version(self) -> Optional[str]:
        if self.context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return self.latest_python_version
        return None

    async def get_current_base_image_version(self) -> Optional[str]:
        current_metadata = await self.get_current_metadata()
        return current_metadata.get("data", {}).get("connectorBuildOptions", {}).get("baseImage")

    async def get_updated_metadata(self) -> str:
        current_metadata = await self.get_current_metadata()
        current_connector_build_options = current_metadata["data"].get("connectorBuildOptions", {})
        current_metadata["data"]["connectorBuildOptions"] = {
            **current_connector_build_options,
            **{"baseImage": self.latest_base_image_version},
        }
        return yaml.safe_dump(current_metadata)

    async def make_connector_change(self) -> StepResult:
        if self.context.connector.language is ConnectorLanguage.JAVA:
            return StepResult(
                self, StepStatus.SKIPPED, stdout="Java connectors are not supported yet", output_artifact=self.container_with_airbyte_repo
            )
        current_base_image_version = await self.get_current_base_image_version()
        if current_base_image_version is None and not self.set_if_not_exists:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a base image metadata field.",
                output_artifact=self.container_with_airbyte_repo,
            )
        if current_base_image_version == self.latest_python_version:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector already uses latest base image",
                output_artifact=self.container_with_airbyte_repo,
            )
        container_with_updated_metadata = await self.get_container_with_updated_metadata(self.container_with_airbyte_repo)

        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated base image to {self.latest_base_image_version} in metadata.yaml",
            output_artifact=container_with_updated_metadata,
        )


class DeleteDockerFile(ConnectorChangeStep):
    title = "Delete Dockerfile"

    async def make_connector_change(self) -> StepResult:
        docker_file_path = self.context.connector.code_directory / "Dockerfile"
        if not docker_file_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a Dockerfile",
                output_artifact=self.container_with_airbyte_repo,
            )
        # As this is a deletion of a file, this has to happen on the host fs
        # Deleting the file in the container would not work because the directory.export method would not export the deleted file from container back to host.
        docker_file_path.unlink()
        self.container_with_airbyte_repo = await self.container_with_airbyte_repo.with_exec(["rm", str(docker_file_path)])
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout="Deleted Dockerfile",
            output_artifact=self.container_with_airbyte_repo,
        )


class AddBuildInstructionsToDoc(ConnectorChangeStep):
    title = "Add build instructions to doc"

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
            updated_doc = self.add_build_instructions(doc_path.read_text())
        except Exception as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr=f"Could not add the build instructions: {e}",
                output_artifact=self.container_with_airbyte_repo,
            )
        self.container_with_airbyte_repo = await self.container_with_airbyte_repo.with_new_file(str(doc_path), updated_doc)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output_artifact=self.container_with_airbyte_repo,
        )

    def add_build_instructions(self, og_doc_content) -> str:
        line_no_for_build_instructions = None
        og_lines = og_doc_content.splitlines()
        for line_no, line in enumerate(og_lines):
            if "## Build instructions" in line:
                return og_doc_content
            if "## Changelog" in line:
                line_no_for_build_instructions = line_no
        if line_no_for_build_instructions is None:
            line_no_for_build_instructions = len(og_lines) - 1

        build_instructions_template = Template(
            textwrap.dedent(
                """
            ## Build instructions
            ### Build your own connector image
            This connector is built using our dynamic built process.
            The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
            The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
            It does not rely on a Dockerfile.

            If you would like to patch our connector and build your own a simple approach would be:

            1. Create your own Dockerfile based on the latest version of the connector image.
            ```Dockerfile
            FROM {{ connector_image }}:latest

            COPY . ./airbyte/integration_code
            RUN pip install ./airbyte/integration_code

            # The entrypoint and default env vars are already set in the base image
            # ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
            # ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
            ```
            Please use this as an example. This is not optimized.

            2. Build your image:
            ```bash
            docker build -t {{ connector_image }}:dev .
            # Running the spec command against your patched connector
            docker run {{ connector_image }}:dev spec
            ```

            ### Customizing our build process
            When contributing on our connector you might need to customize the build process to add a system dependency or set an env var.
            You can customize our build process by adding a `build_customization.py` module to your connector.
            This module should contain a `pre_connector_install` and `post_connector_install` async function that will mutate the base image and the connector container respectively.
            It will be imported at runtime by our build process and the functions will be called if they exist.

            Here is an example of a `build_customization.py` module:
            ```python
            from __future__ import annotations

            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                # Feel free to check the dagger documentation for more information on the Container object and its methods.
                # https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/
                from dagger import Container


            async def pre_connector_install(base_image_container: Container) -> Container:
                return await base_image_container.with_env_variable("MY_PRE_BUILD_ENV_VAR", "my_pre_build_env_var_value")

            async def post_connector_install(connector_container: Container) -> Container:
                return await connector_container.with_env_variable("MY_POST_BUILD_ENV_VAR", "my_post_build_env_var_value")
            ```
            """
            )
        )

        build_instructions = build_instructions_template.render({"connector_image": self.context.connector.metadata["dockerRepository"]})

        new_doc = "\n".join(og_lines[:line_no_for_build_instructions] + [build_instructions] + og_lines[line_no_for_build_instructions:])
        return new_doc


async def run_connector_base_image_upgrade_pipeline(
    context: ConnectorContext, semaphore, commit_and_push: bool, export_changes_to_host: bool, set_if_exists: bool
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
            update_base_image_in_metadata = UpgradeBaseImageMetadata(
                context,
                commit=commit_and_push,
                push=commit_and_push,
                export_changes_to_host=export_changes_to_host,
                set_if_not_exists=set_if_exists,
            )
            update_base_image_in_metadata_result = await update_base_image_in_metadata.run()
            steps_results.append(update_base_image_in_metadata_result)
            context.report = ConnectorReport(context, steps_results, name="BASE IMAGE UPGRADE RESULTS")
    return context.report


async def run_connector_migration_to_base_image_pipeline(
    context: ConnectorContext, semaphore, commit_and_push: bool, export_changes_to_host: bool, pull_request_number: str
):
    async with semaphore:
        steps_results = []
        async with context:
            update_base_image_in_metadata = UpgradeBaseImageMetadata(
                context,
                commit=commit_and_push,
                push=commit_and_push,
                export_changes_to_host=export_changes_to_host,
                set_if_not_exists=True,
            )
            update_base_image_in_metadata_result = await update_base_image_in_metadata.run()
            steps_results.append(update_base_image_in_metadata_result)
            if update_base_image_in_metadata_result.status is not StepStatus.SUCCESS:
                context.report = ConnectorReport(context, steps_results, name="BASE IMAGE UPGRADE RESULTS")
                return context.report

            delete_docker_file = DeleteDockerFile(
                context,
                container_with_airbyte_repo=update_base_image_in_metadata_result.output_artifact,
                commit=commit_and_push,
                push=commit_and_push,
                export_changes_to_host=export_changes_to_host,
            )
            delete_docker_file_result = await delete_docker_file.run()

            steps_results.append(delete_docker_file_result)

            new_version = get_bumped_version(context.connector.version, "minor")
            bump_version_in_metadata = BumpDockerImageTagInMetadata(
                context,
                new_version,
                export_changes_to_host,
                container_with_airbyte_repo=delete_docker_file_result.output_artifact,
                commit=commit_and_push,
                push=commit_and_push,
            )
            bump_version_in_metadata_result = await bump_version_in_metadata.run()
            steps_results.append(bump_version_in_metadata_result)

            add_changelog_entry = AddChangelogEntry(
                context,
                new_version,
                "Use our base image and remove Dockerfile",
                pull_request_number,
                export_changes_to_host,
                container_with_airbyte_repo=bump_version_in_metadata_result.output_artifact,
                commit=commit_and_push,
                push=commit_and_push,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)

            add_build_instructions_to_doc = AddBuildInstructionsToDoc(
                context,
                container_with_airbyte_repo=add_changelog_entry_result.output_artifact,
                commit=commit_and_push,
                push=commit_and_push,
                export_changes_to_host=export_changes_to_host,
            )
            add_build_instructions_to_doc_results = await add_build_instructions_to_doc.run()
            steps_results.append(add_build_instructions_to_doc_results)
            context.report = ConnectorReport(context, steps_results, name="MIGRATE TO BASE IMAGE RESULTS")
    return context.report
