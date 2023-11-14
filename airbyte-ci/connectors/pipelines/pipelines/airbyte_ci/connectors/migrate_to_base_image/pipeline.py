#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import textwrap
from copy import deepcopy
from typing import Optional

from base_images import version_registry
from connector_ops.utils import ConnectorLanguage
from dagger import Directory
from jinja2 import Template
from pipelines.airbyte_ci.connectors.bump_version.pipeline import AddChangelogEntry, BumpDockerImageTagInMetadata, get_bumped_version
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers import git
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus


class UpgradeBaseImageMetadata(Step):
    title = "Upgrade the base image to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Directory,
        set_if_not_exists: bool = True,
    ):
        super().__init__(context)
        self.repo_dir = repo_dir
        self.set_if_not_exists = set_if_not_exists

    async def get_latest_base_image_address(self) -> Optional[str]:
        try:
            version_registry_for_language = await version_registry.get_registry_for_language(
                self.dagger_client, self.context.connector.language, (self.context.docker_hub_username, self.context.docker_hub_password)
            )
            return version_registry_for_language.latest_not_pre_released_published_entry.published_docker_image.address
        except NotImplementedError:
            return None

    @staticmethod
    def update_base_image_in_metadata(current_metadata: dict, latest_base_image_version_address: str) -> dict:
        current_connector_build_options = current_metadata["data"].get("connectorBuildOptions", {})
        updated_metadata = deepcopy(current_metadata)
        updated_metadata["data"]["connectorBuildOptions"] = {
            **current_connector_build_options,
            **{"baseImage": latest_base_image_version_address},
        }
        return updated_metadata

    async def _run(self) -> StepResult:
        latest_base_image_address = await self.get_latest_base_image_address()
        if latest_base_image_address is None:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Could not find a base image for this connector language.",
                output_artifact=self.repo_dir,
            )

        metadata_path = self.context.connector.metadata_file_path
        current_metadata = await metadata_change_helpers.get_current_metadata(self.repo_dir, metadata_path)
        current_base_image_address = current_metadata.get("data", {}).get("connectorBuildOptions", {}).get("baseImage")

        if current_base_image_address is None and not self.set_if_not_exists:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a base image metadata field.",
                output_artifact=self.repo_dir,
            )

        if current_base_image_address == latest_base_image_address:
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector already uses latest base image",
                output_artifact=self.repo_dir,
            )
        updated_metadata = self.update_base_image_in_metadata(current_metadata, latest_base_image_address)
        updated_repo_dir = metadata_change_helpers.get_repo_dir_with_updated_metadata(self.repo_dir, metadata_path, updated_metadata)

        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated base image to {latest_base_image_address} in {metadata_path}",
            output_artifact=updated_repo_dir,
        )


class DeleteConnectorFile(Step):
    def __init__(
        self,
        context: ConnectorContext,
        file_to_delete: str,
    ):
        super().__init__(context)
        self.file_to_delete = file_to_delete

    @property
    def title(self):
        return f"Delete {self.file_to_delete}"

    async def _run(self) -> StepResult:
        file_to_delete_path = self.context.connector.code_directory / self.file_to_delete
        if not file_to_delete_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout=f"Connector does not have a {self.file_to_delete}",
            )
        # As this is a deletion of a file, this has to happen on the host fs
        # Deleting the file in a Directory container would not work because the directory.export method would not export the deleted file from the Directory back to host.
        file_to_delete_path.unlink()
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Deleted {file_to_delete_path}",
        )


class AddBuildInstructionsToReadme(Step):
    title = "Add build instructions to README.md"

    def __init__(self, context: PipelineContext, repo_dir: Directory) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir

    async def _run(self) -> StepResult:
        readme_path = self.context.connector.code_directory / "README.md"
        if not readme_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output_artifact=self.repo_dir,
            )
        current_readme = await (await self.context.get_connector_dir(include=["README.md"])).file("README.md").contents()
        try:
            updated_readme = self.add_build_instructions(current_readme)
        except Exception as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stdout=str(e),
                output_artifact=self.repo_dir,
            )
        updated_repo_dir = await self.repo_dir.with_new_file(str(readme_path), updated_readme)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Added build instructions to {readme_path}",
            output_artifact=updated_repo_dir,
        )

    def add_build_instructions(self, og_doc_content) -> str:

        build_instructions_template = Template(
            textwrap.dedent(
                """

            #### Use `airbyte-ci` to build your connector
            The Airbyte way of building this connector is to use our `airbyte-ci` tool.
            You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
            Then running the following command will build your connector:

            ```bash
            airbyte-ci connectors --name {{ connector_technical_name }} build
            ```
            Once the command is done, you will find your connector image in your local docker registry: `{{ connector_image }}:dev`.

            ##### Customizing our build process
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

            #### Build your own connector image
            This connector is built using our dynamic built process in `airbyte-ci`.
            The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
            The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
            It does not rely on a Dockerfile.

            If you would like to patch our connector and build your own a simple approach would be to:

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
            """
            )
        )

        build_instructions = build_instructions_template.render(
            {
                "connector_image": self.context.connector.metadata["dockerRepository"],
                "connector_technical_name": self.context.connector.technical_name,
            }
        )

        og_lines = og_doc_content.splitlines()
        build_instructions_index = None
        run_instructions_index = None

        for line_no, line in enumerate(og_lines):
            if "#### Build" in line:
                build_instructions_index = line_no
            if "#### Run" in line:
                run_instructions_index = line_no
                break

        if build_instructions_index is None or run_instructions_index is None:
            raise Exception("Could not find build or run instructions in README.md")

        new_doc = "\n".join(og_lines[:build_instructions_index] + build_instructions.splitlines() + og_lines[run_instructions_index:])
        return new_doc


async def run_connector_base_image_upgrade_pipeline(context: ConnectorContext, semaphore, set_if_not_exists: bool) -> ConnectorReport:
    """Run a pipeline to upgrade for a single connector to use our base image."""
    async with semaphore:
        steps_results = []
        async with context:
            og_repo_dir = await context.get_repo_dir()
            update_base_image_in_metadata = UpgradeBaseImageMetadata(
                context,
                og_repo_dir,
                set_if_not_exists=set_if_not_exists,
            )
            update_base_image_in_metadata_result = await update_base_image_in_metadata.run()
            steps_results.append(update_base_image_in_metadata_result)
            final_repo_dir = update_base_image_in_metadata_result.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            context.report = ConnectorReport(context, steps_results, name="BASE IMAGE UPGRADE RESULTS")
    return context.report


async def run_connector_migration_to_base_image_pipeline(context: ConnectorContext, semaphore, pull_request_number: str):
    async with semaphore:
        steps_results = []
        async with context:
            # DELETE DOCKERFILE
            delete_docker_file = DeleteConnectorFile(
                context,
                "Dockerfile",
            )
            delete_docker_file_result = await delete_docker_file.run()
            steps_results.append(delete_docker_file_result)

            # DELETE BUILD.GRADLE IF NOT JAVA
            if context.connector.language is not ConnectorLanguage.JAVA:
                delete_gradle_file = DeleteConnectorFile(
                    context,
                    "build.gradle",
                )
                delete_gradle_file_result = await delete_gradle_file.run()
                steps_results.append(delete_gradle_file_result)

            og_repo_dir = await context.get_repo_dir()

            # UPDATE BASE IMAGE IN METADATA
            update_base_image_in_metadata = UpgradeBaseImageMetadata(
                context,
                og_repo_dir,
                set_if_not_exists=True,
            )
            update_base_image_in_metadata_result = await update_base_image_in_metadata.run()
            steps_results.append(update_base_image_in_metadata_result)
            if update_base_image_in_metadata_result.status is not StepStatus.SUCCESS:
                context.report = ConnectorReport(context, steps_results, name="BASE IMAGE UPGRADE RESULTS")
                return context.report

            # BUMP CONNECTOR VERSION IN METADATA
            new_version = get_bumped_version(context.connector.version, "patch")
            bump_version_in_metadata = BumpDockerImageTagInMetadata(
                context,
                update_base_image_in_metadata_result.output_artifact,
                new_version,
            )
            bump_version_in_metadata_result = await bump_version_in_metadata.run()
            steps_results.append(bump_version_in_metadata_result)

            # ADD CHANGELOG ENTRY
            add_changelog_entry = AddChangelogEntry(
                context,
                bump_version_in_metadata_result.output_artifact,
                new_version,
                "Base image migration: remove Dockerfile and use the python-connector-base image",
                pull_request_number,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)

            # UPDATE DOC
            add_build_instructions_to_doc = AddBuildInstructionsToReadme(
                context,
                add_changelog_entry_result.output_artifact,
            )
            add_build_instructions_to_doc_results = await add_build_instructions_to_doc.run()
            steps_results.append(add_build_instructions_to_doc_results)

            # EXPORT MODIFIED FILES BACK TO HOST
            final_repo_dir = add_build_instructions_to_doc_results.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))

            context.report = ConnectorReport(context, steps_results, name="MIGRATE TO BASE IMAGE RESULTS")
    return context.report
