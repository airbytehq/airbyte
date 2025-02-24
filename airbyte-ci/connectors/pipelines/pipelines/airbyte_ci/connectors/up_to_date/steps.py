#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import dagger
from connector_ops.utils import POETRY_LOCK_FILE_NAME, PYPROJECT_FILE_NAME  # type: ignore
from deepdiff import DeepDiff  # type: ignore

from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.models.steps import Step, StepModifyingFiles, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import List


class PoetryUpdate(StepModifyingFiles):
    context: ConnectorContext
    dev: bool
    specified_versions: dict[str, str]
    title = "Update versions of libraries in poetry."

    def __init__(
        self,
        context: PipelineContext,
        connector_directory: dagger.Directory,
        dev: bool = False,
        specific_dependencies: List[str] | None = None,
    ) -> None:
        super().__init__(context, connector_directory)
        self.dev = dev
        self.specified_versions = self.parse_specific_dependencies(specific_dependencies) if specific_dependencies else {}

    @staticmethod
    def parse_specific_dependencies(specific_dependencies: List[str]) -> dict[str, str]:
        package_name_pattern = r"^(\w+)[@><=]([^\s]+)$"
        versions: dict[str, str] = {}
        for dep in specific_dependencies:
            match = re.match(package_name_pattern, dep)
            if match:
                package = match.group(1)
                versions[package] = dep
            else:
                raise ValueError(f"Invalid dependency name: {dep}")
        return versions

    async def _run(self) -> StepResult:
        connector_directory = self.modified_directory
        if PYPROJECT_FILE_NAME not in await connector_directory.entries():
            return StepResult(step=self, status=StepStatus.SKIPPED, stderr=f"Connector does not have a {PYPROJECT_FILE_NAME}")

        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image_name)
        connector_container = base_container.with_mounted_directory("/connector", connector_directory).with_workdir("/connector")
        original_poetry_lock = await connector_container.file(POETRY_LOCK_FILE_NAME).contents()
        original_pyproject_file = await connector_container.file(PYPROJECT_FILE_NAME).contents()

        try:
            for package, version in self.specified_versions.items():
                if not self.dev:
                    self.logger.info(f"Add {package} {version} to main dependencies")
                    connector_container = await connector_container.with_exec(["poetry", "add", f"{package}{version}"], use_entrypoint=True)
                else:
                    self.logger.info(f"Add {package} {version} to dev dependencies")
                    connector_container = await connector_container.with_exec(
                        ["poetry", "add", f"{package}{version}", "--group=dev"], use_entrypoint=True
                    )

            connector_container = await connector_container.with_exec(["poetry", "update"], use_entrypoint=True)
            self.logger.info(await connector_container.stdout())
        except dagger.ExecError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))

        if (
            original_poetry_lock != await connector_container.file(POETRY_LOCK_FILE_NAME).contents()
            or original_pyproject_file != await connector_container.file(PYPROJECT_FILE_NAME).contents()
        ):
            self.modified_directory = await connector_container.directory(".")
            self.modified_files = [POETRY_LOCK_FILE_NAME, PYPROJECT_FILE_NAME]
            return StepResult(step=self, status=StepStatus.SUCCESS, output=connector_container.directory("."))

        return StepResult(step=self, status=StepStatus.SKIPPED, stdout="No changes in poetry.lock or pyproject.toml")


class DependencyUpdateType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    UPDATED = "updated"


@dataclass
class DependencyUpdate:
    package_type: str
    package_name: str
    update_type: DependencyUpdateType
    new_version: str | None = None
    previous_version: str | None = None


class GetDependencyUpdates(Step):
    SYFT_DOCKER_IMAGE = "anchore/syft:v1.6.0"
    context: ConnectorContext
    title: str = "Get dependency updates"

    def get_syft_container(self) -> dagger.Container:
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, ".docker", "config.json")
        config_file = self.dagger_client.host().file(config_path)
        return (
            self.dagger_client.container()
            .from_(self.SYFT_DOCKER_IMAGE)
            .with_mounted_file("/config/config.json", config_file)
            .with_env_variable("DOCKER_CONFIG", "/config")
            # Syft requires access to the docker daemon. We share the host's docker socket with the Syft container.
            .with_unix_socket("/var/run/docker.sock", self.dagger_client.host().unix_socket("/var/run/docker.sock"))
        )

    @property
    def latest_connector_docker_image_address(self) -> str:
        docker_image_name = self.context.connector.metadata["dockerRepository"]
        return f"{docker_image_name}:latest"

    async def get_sbom_from_latest_image(self) -> str:
        syft_container = self.get_syft_container()
        return await syft_container.with_exec([self.latest_connector_docker_image_address, "-o", "syft-json"], use_entrypoint=True).stdout()

    async def get_sbom_from_container(self, container: dagger.Container) -> str:
        oci_tarball_path = Path(f"/tmp/{self.context.connector.technical_name}-{self.context.connector.version}.tar")
        await container.export(str(oci_tarball_path))
        syft_container = self.get_syft_container()
        container_sbom = await (
            syft_container.with_mounted_file("/tmp/oci.tar", self.dagger_client.host().file(str(oci_tarball_path)))
            .with_exec(["/tmp/oci.tar", "-o", "syft-json"], use_entrypoint=True)
            .stdout()
        )
        oci_tarball_path.unlink()
        return container_sbom

    def get_dependency_updates(self, raw_latest_sbom: str, raw_current_sbom: str) -> List[DependencyUpdate]:
        latest_sbom = json.loads(raw_latest_sbom)
        current_sbom = json.loads(raw_current_sbom)
        latest_packages = {(dep["type"], dep["name"]): dep["version"] for dep in latest_sbom["artifacts"]}
        current_packages = {(dep["type"], dep["name"]): dep["version"] for dep in current_sbom["artifacts"]}
        diff = DeepDiff(latest_packages, current_packages)
        dependency_updates = []
        diff_type_to_update_type = [
            ("values_changed", DependencyUpdateType.UPDATED),
            ("dictionary_item_added", DependencyUpdateType.ADDED),
            ("dictionary_item_removed", DependencyUpdateType.REMOVED),
        ]
        for diff_type, update_type in diff_type_to_update_type:
            for change in diff.tree.get(diff_type, []):
                package_type, package_name = change.get_root_key()
                previous_version, new_version = change.t1, change.t2
                dependency_updates.append(
                    DependencyUpdate(package_type, package_name, update_type, previous_version=previous_version, new_version=new_version)
                )
        return dependency_updates

    async def _run(self, target_connector_container: dagger.Container) -> StepResult:
        latest_sbom = await self.get_sbom_from_latest_image()
        current_sbom = await self.get_sbom_from_container(target_connector_container)
        dependency_updates = self.get_dependency_updates(latest_sbom, current_sbom)
        return StepResult(step=self, status=StepStatus.SUCCESS, output=dependency_updates)
