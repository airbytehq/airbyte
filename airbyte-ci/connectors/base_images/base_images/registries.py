#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type

import dagger
import semver
from base_images import consts
from base_images.common import AirbyteConnectorBaseImage, PublishedImage
from base_images.python.bases import AirbytePythonConnectorBaseImage
from connector_ops.utils import ConnectorLanguage  # type: ignore

MANAGED_BASE_IMAGES = [AirbytePythonConnectorBaseImage]


@dataclass
class PublishedBaseImage(PublishedImage):
    @property
    def version(self) -> semver.VersionInfo:
        return semver.VersionInfo.parse(self.tag)


@dataclass
class ChangelogEntry:
    version: semver.VersionInfo
    changelog_entry: str
    dockerfile_example: str

    def to_serializable_dict(self):
        return {
            "version": str(self.version),
            "changelog_entry": self.changelog_entry,
            "dockerfile_example": self.dockerfile_example,
        }

    @staticmethod
    def from_dict(entry_dict: Dict):
        return ChangelogEntry(
            version=semver.VersionInfo.parse(entry_dict["version"]),
            changelog_entry=entry_dict["changelog_entry"],
            dockerfile_example=entry_dict["dockerfile_example"],
        )


@dataclass
class RegistryEntry:
    published_docker_image: Optional[PublishedBaseImage]
    changelog_entry: Optional[ChangelogEntry]
    version: semver.VersionInfo

    @property
    def published(self) -> bool:
        return self.published_docker_image is not None


class VersionRegistry:
    def __init__(
        self,
        ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage],
        entries: List[RegistryEntry],
    ) -> None:
        self.ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage] = ConnectorBaseImageClass
        self._entries: List[RegistryEntry] = entries

    @staticmethod
    def get_changelog_dump_path(ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage]) -> Path:
        """Returns the path where the changelog is dumped to disk.

        Args:
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            Path: The path where the changelog JSON is dumped to disk.
        """
        registries_dir = Path("generated/changelogs")
        registries_dir.mkdir(exist_ok=True, parents=True)
        return registries_dir / f'{ConnectorBaseImageClass.image_name.replace("-", "_").replace("/", "_")}.json'  # type: ignore

    @property
    def changelog_dump_path(self) -> Path:
        """Returns the path where the changelog JSON is dumped to disk.

        Returns:
            Path: The path where the changelog JSON is dumped to disk.
        """
        return self.get_changelog_dump_path(self.ConnectorBaseImageClass)

    @staticmethod
    async def get_published_base_images(
        ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage], dagger_client: dagger.Client, docker_credentials: Tuple[str, str]
    ) -> List[PublishedBaseImage]:
        repository_address = f"{consts.REMOTE_REGISTRY}/{ConnectorBaseImageClass.image_name}"
        dockerhub_username_secret = dagger_client.set_secret("DOCKER_HUB_USERNAME", docker_credentials[0])
        dockerhub_username_password = dagger_client.set_secret("DOCKER_HUB_PASSWORD", docker_credentials[1])
        crane_container = (
            dagger_client.container()
            .from_(consts.CRANE_IMAGE_ADDRESS)
            .with_secret_variable("DOCKER_HUB_USERNAME", dockerhub_username_secret)
            .with_secret_variable("DOCKER_HUB_PASSWORD", dockerhub_username_password)
            .with_exec(
                ["sh", "-c", "crane auth login index.docker.io -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"], skip_entrypoint=True
            )
            .with_env_variable("CACHE_BUSTER", str(uuid.uuid4()))
        )
        try:
            ls_output = await crane_container.with_exec(["ls", repository_address]).stdout()
        except dagger.ExecError as exec_error:
            if "NAME_UNKNOWN" in exec_error.stderr:
                ls_output = ""
            else:
                raise exec_error
        available_addresses_without_digest = [f"{repository_address}:{tag}" for tag in ls_output.splitlines()]
        available_addresses_with_digest = []
        for address in available_addresses_without_digest:
            digest = (await crane_container.with_exec(["digest", address]).stdout()).strip()
            available_addresses_with_digest.append(f"{address}@{digest}")
        return [PublishedBaseImage.from_address(address) for address in available_addresses_with_digest]

    @staticmethod
    async def load(
        ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage], dagger_client: dagger.Client, docker_credentials: Tuple[str, str]
    ) -> VersionRegistry:
        """Instantiates a registry by fetching available versions from the remote registry and loading the changelog from disk.

        Args:
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            VersionRegistry: The registry.
        """
        change_log_dump_path = VersionRegistry.get_changelog_dump_path(ConnectorBaseImageClass)
        if not change_log_dump_path.exists():
            changelog_entries = []
        else:
            changelog_entries = [ChangelogEntry.from_dict(raw_entry) for raw_entry in json.loads(change_log_dump_path.read_text())]
        changelog_entries_by_version = {entry.version: entry for entry in changelog_entries}
        published_docker_images = await VersionRegistry.get_published_base_images(
            ConnectorBaseImageClass, dagger_client, docker_credentials
        )
        published_docker_images_by_version = {image.version: image for image in published_docker_images}
        all_versions = set(changelog_entries_by_version.keys()) | set(published_docker_images_by_version.keys())
        registry_entries = []
        for version in all_versions:
            published_docker_image = published_docker_images_by_version.get(version)
            changelog_entry = changelog_entries_by_version.get(version)
            registry_entries.append(RegistryEntry(published_docker_image, changelog_entry, version))
        return VersionRegistry(ConnectorBaseImageClass, registry_entries)

    def save_changelog(self):
        """Writes the changelog to disk. The changelog is dumped as a json file with a list of ChangelogEntry objects."""
        as_json = json.dumps([entry.changelog_entry.to_serializable_dict() for entry in self.entries if entry.changelog_entry])
        self.changelog_dump_path.write_text(as_json)

    def add_entry(self, new_entry: RegistryEntry) -> List[RegistryEntry]:
        """Registers a new entry in the registry.

        Args:
            new_entry (RegistryEntry): The new entry to register.

        Returns:
            List[RegistryEntry]: All the entries sorted by version number in descending order.
        """
        self._entries.append(new_entry)
        self.save_changelog()
        return self.entries

    @property
    def entries(self) -> List[RegistryEntry]:
        """Returns all the base image versions sorted by version number in descending order.

        Returns:
            List[Type[RegistryEntry]]: All the published versions sorted by version number in descending order.
        """
        return sorted(self._entries, key=lambda entry: entry.version, reverse=True)

    @property
    def latest_entry(self) -> Optional[RegistryEntry]:
        """Returns the latest entry this registry.
        The latest entry is the one with the highest version number.
        If no entry is available, returns None.
        Returns:
            Optional[RegistryEntry]: The latest registry entry, or None if no entry is available.
        """
        try:
            return self.entries[0]
        except IndexError:
            return None

    def get_entry_for_version(self, version: semver.VersionInfo) -> Optional[RegistryEntry]:
        """Returns the entry for a given version.
        If no entry is available, returns None.
        Returns:
            Optional[RegistryEntry]: The registry entry for the given version, or None if no entry is available.
        """
        for entry in self.entries:
            if entry.version == version:
                return entry
        return None

    @property
    def latest_not_pre_released_entry(self) -> Optional[RegistryEntry]:
        """Returns the latest entry with a not pre-released version in this registry.
        If no entry is available, returns None.
        Returns:
            Optional[RegistryEntry]: The latest registry entry with a not pre-released version, or None if no entry is available.
        """
        try:
            not_pre_release_published_entries = [entry for entry in self.entries if not entry.version.prerelease and entry.published]
            return not_pre_release_published_entries[0]
        except IndexError:
            return None


async def get_python_registry(dagger_client: dagger.Client, docker_credentials: Tuple[str, str]) -> VersionRegistry:
    return await VersionRegistry.load(AirbytePythonConnectorBaseImage, dagger_client, docker_credentials)


async def get_registry_for_language(
    dagger_client: dagger.Client, language: ConnectorLanguage, docker_credentials: Tuple[str, str]
) -> VersionRegistry:
    if language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
        return await get_python_registry(dagger_client, docker_credentials)
    else:
        raise NotImplementedError(f"Registry for language {language} is not implemented yet.")


async def get_all_registries(dagger_client: dagger.Client, docker_credentials: Tuple[str, str]) -> List[VersionRegistry]:
    return [
        await get_python_registry(dagger_client, docker_credentials),
        # await get_java_registry(dagger_client),
    ]
