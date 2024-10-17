#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Tuple, Type

import dagger
import semver
from base_images import consts, published_image
from base_images.bases import AirbyteConnectorBaseImage
from base_images.python.bases import AirbyteManifestOnlyConnectorBaseImage, AirbytePythonConnectorBaseImage
from base_images.utils import docker
from connector_ops.utils import ConnectorLanguage  # type: ignore

MANAGED_BASE_IMAGES = [AirbytePythonConnectorBaseImage]


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
class VersionRegistryEntry:
    published_docker_image: Optional[published_image.PublishedImage]
    changelog_entry: Optional[ChangelogEntry]
    version: semver.VersionInfo

    @property
    def published(self) -> bool:
        return self.published_docker_image is not None


class VersionRegistry:
    def __init__(
        self,
        ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage],
        entries: List[VersionRegistryEntry],
    ) -> None:
        self.ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage] = ConnectorBaseImageClass
        self._entries: List[VersionRegistryEntry] = entries

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
        return registries_dir / f'{ConnectorBaseImageClass.repository.replace("-", "_").replace("/", "_")}.json'  # type: ignore

    @property
    def changelog_dump_path(self) -> Path:
        """Returns the path where the changelog JSON is dumped to disk.

        Returns:
            Path: The path where the changelog JSON is dumped to disk.
        """
        return self.get_changelog_dump_path(self.ConnectorBaseImageClass)

    @staticmethod
    def get_changelog_entries(ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage]) -> List[ChangelogEntry]:
        """Returns the changelog entries for a given base image version class.
        The changelog entries are loaded from the checked in changelog dump JSON file.

        Args:
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            List[ChangelogEntry]: The changelog entries for a given base image version class.
        """
        change_log_dump_path = VersionRegistry.get_changelog_dump_path(ConnectorBaseImageClass)
        if not change_log_dump_path.exists():
            changelog_entries = []
        else:
            changelog_entries = [ChangelogEntry.from_dict(raw_entry) for raw_entry in json.loads(change_log_dump_path.read_text())]
        return changelog_entries

    @staticmethod
    async def get_all_published_base_images(
        dagger_client: dagger.Client, docker_credentials: Tuple[str, str], ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage]
    ) -> List[published_image.PublishedImage]:
        """Returns all the published base images for a given base image version class.

        Args:
            dagger_client (dagger.Client): The dagger client used to build the registry.
            docker_credentials (Tuple[str, str]): The docker credentials used to fetch published images from DockerHub.
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            List[published_image.PublishedImage]: The published base images for a given base image version class.
        """
        crane_client = docker.CraneClient(dagger_client, docker_credentials)
        remote_registry = docker.RemoteRepository(crane_client, consts.REMOTE_REGISTRY, ConnectorBaseImageClass.repository)  # type: ignore
        return await remote_registry.get_all_images()

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
        # Loading the local structured changelog file which is stored as a json file.
        changelog_entries = VersionRegistry.get_changelog_entries(ConnectorBaseImageClass)

        # Build a dict of changelog entries by version number for easier lookup
        changelog_entries_by_version = {entry.version: entry for entry in changelog_entries}

        # Instantiate a crane client and a remote registry to fetch published images from DockerHub
        published_docker_images = await VersionRegistry.get_all_published_base_images(
            dagger_client, docker_credentials, ConnectorBaseImageClass
        )

        # Build a dict of published images by version number for easier lookup
        published_docker_images_by_version = dict()
        for image in published_docker_images:
            try:
                published_docker_images_by_version[image.version] = image
            # Skip any images with invalid version tags (i.e. "test_build")
            except ValueError:
                continue

        # We union the set of versions from the changelog and the published images to get all the versions we have to consider
        all_versions = set(changelog_entries_by_version.keys()) | set(published_docker_images_by_version.keys())

        registry_entries = []
        # Iterate over all the versions we have to consider and build a registry entry for each of them
        # The registry entry will contain the published image if available, and the changelog entry if available
        # If the version is not published, the published image will be None
        # If the version is not in the changelog, the changelog entry will be None
        for version in all_versions:
            published_docker_image = published_docker_images_by_version.get(version)
            changelog_entry = changelog_entries_by_version.get(version)
            registry_entries.append(VersionRegistryEntry(published_docker_image, changelog_entry, version))
        return VersionRegistry(ConnectorBaseImageClass, registry_entries)

    def save_changelog(self):
        """Writes the changelog to disk. The changelog is dumped as a json file with a list of ChangelogEntry objects."""
        as_json = json.dumps([entry.changelog_entry.to_serializable_dict() for entry in self.entries if entry.changelog_entry])
        self.changelog_dump_path.write_text(as_json)

    def add_entry(self, new_entry: VersionRegistryEntry) -> List[VersionRegistryEntry]:
        """Registers a new entry in the registry and saves the changelog locally.

        Args:
            new_entry (VersionRegistryEntry): The new entry to register.

        Returns:
            List[VersionRegistryEntry]: All the entries sorted by version number in descending order.
        """
        self._entries.append(new_entry)
        self.save_changelog()
        return self.entries

    @property
    def entries(self) -> List[VersionRegistryEntry]:
        """Returns all the base image versions sorted by version number in descending order.

        Returns:
            List[Type[VersionRegistryEntry]]: All the published versions sorted by version number in descending order.
        """
        return sorted(self._entries, key=lambda entry: entry.version, reverse=True)

    @property
    def latest_entry(self) -> Optional[VersionRegistryEntry]:
        """Returns the latest entry this registry.
        The latest entry is the one with the highest version number.
        If no entry is available, returns None.
        Returns:
            Optional[VersionRegistryEntry]: The latest registry entry, or None if no entry is available.
        """
        try:
            return self.entries[0]
        except IndexError:
            return None

    @property
    def latest_published_entry(self) -> Optional[VersionRegistryEntry]:
        """Returns the latest published entry this registry.
        The latest published entry is the one with the highest version number among the published entries.
        If no entry is available, returns None.
        Returns:
            Optional[VersionRegistryEntry]: The latest published registry entry, or None if no entry is available.
        """
        try:
            return [entry for entry in self.entries if entry.published][0]
        except IndexError:
            return None

    def get_entry_for_version(self, version: semver.VersionInfo) -> Optional[VersionRegistryEntry]:
        """Returns the entry for a given version.
        If no entry is available, returns None.
        Returns:
            Optional[VersionRegistryEntry]: The registry entry for the given version, or None if no entry is available.
        """
        for entry in self.entries:
            if entry.version == version:
                return entry
        return None

    @property
    def latest_not_pre_released_published_entry(self) -> Optional[VersionRegistryEntry]:
        """Returns the latest entry with a not pre-released version in this registry which is published.
        If no entry is available, returns None.
        It is meant to be used externally to get the latest published version.
        Returns:
            Optional[VersionRegistryEntry]: The latest registry entry with a not pre-released version, or None if no entry is available.
        """
        try:
            not_pre_release_published_entries = [entry for entry in self.entries if not entry.version.prerelease and entry.published]
            return not_pre_release_published_entries[0]
        except IndexError:
            return None


async def get_python_registry(dagger_client: dagger.Client, docker_credentials: Tuple[str, str]) -> VersionRegistry:
    return await VersionRegistry.load(AirbytePythonConnectorBaseImage, dagger_client, docker_credentials)


async def get_manifest_only_registry(dagger_client: dagger.Client, docker_credentials: Tuple[str, str]) -> VersionRegistry:
    return await VersionRegistry.load(AirbyteManifestOnlyConnectorBaseImage, dagger_client, docker_credentials)


async def get_registry_for_language(
    dagger_client: dagger.Client, language: ConnectorLanguage, docker_credentials: Tuple[str, str]
) -> VersionRegistry:
    """Returns the registry for a given language.
    It is meant to be used externally to get the registry for a given connector language.

    Args:
        dagger_client (dagger.Client): The dagger client used to build the registry.
        language (ConnectorLanguage): The connector language.
        docker_credentials (Tuple[str, str]): The docker credentials used to fetch published images from DockerHub.

    Raises:
        NotImplementedError: Raised if the registry for the given language is not implemented yet.

    Returns:
        VersionRegistry: The registry for the given language.
    """
    if language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
        return await get_python_registry(dagger_client, docker_credentials)
    elif language is ConnectorLanguage.MANIFEST_ONLY:
        return await get_manifest_only_registry(dagger_client, docker_credentials)
    else:
        raise NotImplementedError(f"Registry for language {language} is not implemented yet.")


async def get_all_registries(dagger_client: dagger.Client, docker_credentials: Tuple[str, str]) -> List[VersionRegistry]:
    return [
        await get_python_registry(dagger_client, docker_credentials),
        # await get_java_registry(dagger_client),
    ]
