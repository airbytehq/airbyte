# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import dagger
import semver
import yaml
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage  # type: ignore

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.system.docker import with_crane
from pipelines.helpers.connectors.dagger_fs import dagger_read_file, dagger_write_file
from pipelines.models.steps import StepModifyingFiles, StepResult, StepStatus

if TYPE_CHECKING:
    import dagger


class NoBaseImageAddressInMetadataError(Exception):
    pass


class UpdateBaseImageMetadata(StepModifyingFiles):
    BASE_IMAGE_LIST_CACHE_TTL_SECONDS = 60 * 60 * 24  # 1 day

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

    def _get_repository_for_language(self, language: ConnectorLanguage) -> str:
        """Map connector language to DockerHub repository."""
        if language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return "airbyte/python-connector-base"
        elif language is ConnectorLanguage.MANIFEST_ONLY:
            return "airbyte/source-declarative-manifest"
        elif language is ConnectorLanguage.JAVA:
            return "airbyte/java-connector-base"
        else:
            raise NotImplementedError(f"Registry for language {language} is not implemented yet.")

    def _parse_latest_stable_tag(self, tags: List[str]) -> Optional[str]:
        """Parse tags to find latest stable (non-prerelease) version."""
        valid_versions = []
        for tag in tags:
            try:
                version = semver.VersionInfo.parse(tag)
                if not version.prerelease:  # Exclude pre-release versions
                    valid_versions.append(version)
            except ValueError:
                continue  # Skip non-semver tags

        if valid_versions:
            return str(max(valid_versions))
        return None

    async def get_latest_base_image_address(self) -> Optional[str]:
        try:
            if not (self.context.docker_hub_username and self.context.docker_hub_password):
                raise ValueError("Docker Hub credentials are required to get the latest base image address")

            repository = self._get_repository_for_language(self.context.connector.language)
            crane_container = with_crane(self.context)

            # List all tags
            tags_output = await crane_container.with_exec(["crane", "ls", f"docker.io/{repository}"]).stdout()
            tags = [tag.strip() for tag in tags_output.strip().split("\n") if tag.strip()]

            latest_tag = self._parse_latest_stable_tag(tags)
            if latest_tag:
                # Get the digest for the specific tag to ensure immutable reference
                digest_output = await crane_container.with_exec(["crane", "digest", f"docker.io/{repository}:{latest_tag}"]).stdout()
                digest = digest_output.strip()
                return f"docker.io/{repository}:{latest_tag}@{digest}"
            return None
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
        updated_base_image_address = None
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
            updated_base_image_address = latest_base_image_address
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
            output={
                "updated_connector_directory": updated_connector_directory,
                "updated_base_image_address": updated_base_image_address,
            },
        )
