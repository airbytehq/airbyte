# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from base_images import version_registry  # type: ignore
from connector_ops.utils import METADATA_FILE_NAME  # type: ignore
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.connectors.dagger_fs import dagger_read_file, dagger_write_file
from pipelines.models.steps import StepModifyingFiles, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Optional

    import dagger


class NoBaseImageAddressInMetadataError(Exception):
    pass


class UpdateBaseImageMetadata(StepModifyingFiles):
    context: ConnectorContext

    title = "Upgrade the base image to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        connector_directory: dagger.Directory,
        set_if_not_exists: bool = False,
    ) -> None:
        super().__init__(context, connector_directory)
        self.set_if_not_exists = set_if_not_exists
        self.modified_files = []
        self.connector_directory = connector_directory

    async def get_latest_base_image_address(self) -> Optional[str]:
        try:
            if self.context.docker_hub_username is None or self.context.docker_hub_password is None:
                raise ValueError("Docker Hub credentials are required to get the latest base image address")
            version_registry_for_language = await version_registry.get_registry_for_language(
                self.dagger_client,
                self.context.connector.language,
                (self.context.docker_hub_username.value, self.context.docker_hub_password.value),
            )
            return version_registry_for_language.latest_not_pre_released_published_entry.published_docker_image.address
        except NotImplementedError:
            return None

    @staticmethod
    async def update_base_image_in_metadata(
        connector_directory: dagger.Directory, latest_base_image_version_address: str, set_if_not_exists: bool = False
    ) -> dagger.Directory:
        raw_metadata = await dagger_read_file(connector_directory, METADATA_FILE_NAME)
        current_metadata = yaml.safe_load(raw_metadata)

        current_base_image_version_address = current_metadata.get("data").get("connectorBuildOptions", {}).get("baseImage")
        if not current_base_image_version_address:
            if set_if_not_exists:
                current_metadata["data"]["connectorBuildOptions"] = {"baseImage": latest_base_image_version_address}
                new_raw_metadata = yaml.dump(current_metadata)
            else:
                raise NoBaseImageAddressInMetadataError("No base image address found in metadata file")
        else:
            new_raw_metadata = raw_metadata.replace(current_base_image_version_address, latest_base_image_version_address)
        updated_connector_dir = dagger_write_file(connector_directory, METADATA_FILE_NAME, new_raw_metadata)
        return updated_connector_dir

    async def _run(self) -> StepResult:
        latest_base_image_address = await self.get_latest_base_image_address()
        if latest_base_image_address is None:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Could not find a base image for this connector language.",
            )

        current_base_image_address = self.context.connector.metadata.get("connectorBuildOptions", {}).get("baseImage")

        if not self.set_if_not_exists and current_base_image_address is None:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="This connector does not have a base image set in metadata.yaml.",
            )

        if current_base_image_address == latest_base_image_address:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout=f"Base image is already up to date: {latest_base_image_address}",
            )

        original_connector_directory = self.connector_directory or await self.context.get_connector_dir()
        try:
            updated_connector_directory = await self.update_base_image_in_metadata(
                original_connector_directory, latest_base_image_address, self.set_if_not_exists
            )
        except NoBaseImageAddressInMetadataError:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr="No base image address found in metadata file",
            )
        self.modified_files.append(METADATA_FILE_NAME)

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated base image to {latest_base_image_address} in {METADATA_FILE_NAME}",
            output=updated_connector_directory,
        )
