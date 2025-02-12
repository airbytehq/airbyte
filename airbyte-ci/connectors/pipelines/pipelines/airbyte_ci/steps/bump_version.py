#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

import dagger
import semver
import yaml  # type: ignore
from connector_ops.utils import METADATA_FILE_NAME, PYPROJECT_FILE_NAME  # type: ignore

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.connectors.dagger_fs import dagger_read_file, dagger_write_file
from pipelines.models.steps import StepModifyingFiles, StepResult, StepStatus

BUMP_VERSION_METHOD_MAPPING: Mapping[str, Any] = {
    "patch": semver.Version.bump_patch,
    "minor": semver.Version.bump_minor,
    "major": semver.Version.bump_major,
    "rc": semver.Version.bump_prerelease,
}

if TYPE_CHECKING:
    pass


class ConnectorVersionNotFoundError(Exception):
    pass


class PoetryVersionBumpError(Exception):
    pass


class SetConnectorVersion(StepModifyingFiles):
    context: ConnectorContext

    @property
    def title(self) -> str:
        return f"Set connector version to {self.new_version}"

    def __init__(
        self,
        context: ConnectorContext,
        connector_directory: dagger.Directory,
        new_version: str,
    ) -> None:
        super().__init__(context, connector_directory)
        self.new_version = new_version

    @staticmethod
    async def _set_version_in_metadata(new_version: str, connector_directory: dagger.Directory) -> dagger.Directory:
        raw_metadata = await dagger_read_file(connector_directory, METADATA_FILE_NAME)
        current_metadata = yaml.safe_load(raw_metadata)

        try:
            current_version = current_metadata["data"]["dockerImageTag"]
        except KeyError:
            raise ConnectorVersionNotFoundError("dockerImageTag not found in metadata file")

        # We use replace here instead of mutating the deserialized yaml to avoid messing up with the comments in the metadata file.
        new_raw_metadata = raw_metadata.replace("dockerImageTag: " + current_version, "dockerImageTag: " + new_version)
        updated_connector_dir = dagger_write_file(connector_directory, METADATA_FILE_NAME, new_raw_metadata)

        return updated_connector_dir

    @staticmethod
    async def _set_version_in_poetry_package(
        container_with_poetry: dagger.Container, connector_directory: dagger.Directory, new_version: str
    ) -> dagger.Directory:
        try:
            connector_directory_with_updated_pyproject = await (
                container_with_poetry.with_directory("/connector", connector_directory)
                .with_workdir("/connector")
                .with_exec(["poetry", "version", new_version], use_entrypoint=True)
                .directory("/connector")
            )
        except dagger.ExecError as e:
            raise PoetryVersionBumpError(f"Failed to bump version in pyproject.toml: {e}")
        return connector_directory_with_updated_pyproject

    async def _run(self) -> StepResult:
        original_connector_directory = self.modified_directory
        try:
            self.modified_directory = await self._set_version_in_metadata(self.new_version, original_connector_directory)
            self.modified_files.append(METADATA_FILE_NAME)
        except (FileNotFoundError, ConnectorVersionNotFoundError) as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr="Connector does not have a metadata file or the version is not set in the metadata file",
                exc_info=e,
            )

        if self.context.connector.pyproject_file_path.is_file():
            try:
                poetry_container = with_poetry(self.context)
                self.modified_directory = await self._set_version_in_poetry_package(
                    poetry_container, self.modified_directory, self.new_version
                )
                self.modified_files.append(PYPROJECT_FILE_NAME)
            except PoetryVersionBumpError as e:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr="Failed to bump version in pyproject.toml",
                    exc_info=e,
                )

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated connector to {self.new_version}",
            output=self.modified_directory,
        )


class BumpConnectorVersion(SetConnectorVersion):
    def __init__(self, context: ConnectorContext, connector_directory: dagger.Directory, bump_type: str, rc: bool = False) -> None:
        self.bump_type = bump_type
        new_version = self.get_bumped_version(context.connector.version, bump_type, rc)
        super().__init__(
            context,
            connector_directory,
            new_version,
        )

    @property
    def title(self) -> str:
        return f"{self.bump_type.upper()} bump {self.context.connector.technical_name} version to {self.new_version}"

    @staticmethod
    def get_bumped_version(version: str | None, bump_type: str, rc: bool) -> str:
        if version is None:
            raise ValueError("Version is not set")
        current_version = semver.VersionInfo.parse(version)
        if bump_type in BUMP_VERSION_METHOD_MAPPING:
            new_version = BUMP_VERSION_METHOD_MAPPING[bump_type](current_version)
            if rc:
                new_version = new_version.bump_prerelease()
        elif bump_type.startswith("version:"):
            version_str = bump_type.split("version:", 1)[1]
            if semver.VersionInfo.is_valid(version_str):
                return version_str
            else:
                raise ValueError(f"Invalid version: {version_str}")
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")
        return str(new_version)
