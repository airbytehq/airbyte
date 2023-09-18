#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Optional

import yaml
from base_images import python
from connector_ops.utils import ConnectorLanguage
from dagger import Container
from pipelines.bases import ConnectorReport, StepResult, StepStatus
from pipelines.connector_changes.common import MetadataUpdateStep
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
