#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, Optional

import yaml
from base_images import python
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage
from dagger import Container
from pipelines.autocommit.common import AutoCommitStep
from pipelines.bases import StepResult, StepStatus


class UpdateBaseImageInMetadata(AutoCommitStep):
    title = "Update base image to latest version in metadata.yaml"
    latest_python_version = python.VERSION_REGISTRY.latest_version.name_with_tag
    # latest_java_version = java.VERSION_REGISTRY.latest_version

    @property
    def latest_base_image_version(self) -> Optional[str]:
        if self.context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return self.latest_python_version
        return None

    async def _run(self, *args, **kwargs) -> StepResult:
        if self.context.connector.language is ConnectorLanguage.JAVA:
            return StepResult(
                self, StepStatus.SKIPPED, stdout="Java connectors are not supported yet", output_artifact=self.container_with_airbyte_repo
            )
        current_base_image_version = await self.get_current_base_image_version()
        if current_base_image_version is None:
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
        container_with_updated_metadata = await self.commit_all_changes(container_with_updated_metadata)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Updated base image to {self.latest_base_image_version} in metadata.yaml",
            output_artifact=container_with_updated_metadata,
        )

    async def get_current_base_image_version(self) -> Optional[str]:
        current_metadata = await self.get_current_metadata()
        return current_metadata.get("data", {}).get("connectorBuildOptions", {}).get("baseImage")

    async def get_current_metadata(self) -> Dict:
        connector_dir = await self.get_connector_dir()
        return yaml.safe_load(await connector_dir.file(METADATA_FILE_NAME).contents())

    async def get_updated_metadata(self) -> str:
        current_metadata = await self.get_current_metadata()
        current_metadata["data"]["connectorBuildOptions"]["baseImage"] = self.latest_base_image_version
        return yaml.safe_dump(current_metadata)

    async def get_container_with_updated_metadata(self, container_with_airbyte_repo: Container) -> Container:
        new_metadata = await self.get_updated_metadata()
        absolute_path_to_new_metadata = f"/airbyte/{self.context.connector.code_directory}/{METADATA_FILE_NAME}"
        return container_with_airbyte_repo.with_new_file(absolute_path_to_new_metadata, new_metadata)
