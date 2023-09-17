#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import datetime
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type

import semver
from base_images import errors
from base_images.common import AirbyteConnectorBaseImage, PublishedDockerImage
from base_images.python.bases import AirbytePythonConnectorBaseImage
from connector_ops.utils import ConnectorLanguage  # type: ignore


@dataclass
class RegistryEntry:
    published_docker_image: PublishedDockerImage
    changelog_entry: str
    dockerfile_example: str
    published_timestamp: datetime.datetime
    version: semver.VersionInfo

    def to_serializable_dict(self):
        return {
            "published_docker_image": asdict(self.published_docker_image),
            "changelog_entry": self.changelog_entry,
            "dockerfile_example": self.dockerfile_example,
            "published_timestamp": self.published_timestamp.isoformat(),
            "version": str(self.version),
        }

    @staticmethod
    def from_dict(entry_dict: Dict):
        return RegistryEntry(
            published_docker_image=PublishedDockerImage(**entry_dict["published_docker_image"]),
            changelog_entry=entry_dict["changelog_entry"],
            dockerfile_example=entry_dict["dockerfile_example"],
            published_timestamp=datetime.datetime.fromisoformat(entry_dict["published_timestamp"]),
            version=semver.VersionInfo.parse(entry_dict["version"]),
        )


class VersionRegistry:
    def __init__(
        self,
        ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage],
        entries: List[RegistryEntry],
    ) -> None:
        self.ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage] = ConnectorBaseImageClass
        self._entries: List[RegistryEntry] = entries

    @staticmethod
    def get_dump_path(ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage]) -> Path:
        """Returns the path where the registry is dumped to disk.

        Args:
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            Path: The path where the registry is dumped to disk.
        """
        registries_dir = Path("generated/registries")
        registries_dir.mkdir(exist_ok=True, parents=True)
        return registries_dir / f'{ConnectorBaseImageClass.image_name.replace("-", "_").replace("/", "_")}.json'  # type: ignore

    @property
    def dump_path(self) -> Path:
        """Returns the path where the registry is dumped to disk.

        Returns:
            Path: The path where the registry is dumped to disk.
        """
        return self.get_dump_path(self.ConnectorBaseImageClass)

    @property
    def supported_connector_languages(self) -> Tuple[ConnectorLanguage, ...]:
        return self.ConnectorBaseImageClass.compatible_languages  # type: ignore

    @staticmethod
    def load_from_disk(ConnectorBaseImageClass: Type[AirbyteConnectorBaseImage]) -> VersionRegistry:
        """Instantiates a registry from its dump on disk. If the dump does not exist, returns an empty registry.

        Args:
            ConnectorBaseImageClass (Type[AirbyteConnectorBaseImage]): The base image version class bound to the registry.

        Returns:
            VersionRegistry: The registry, loaded from the json file.
        """
        dump_path = VersionRegistry.get_dump_path(ConnectorBaseImageClass)
        if not dump_path.exists():
            return VersionRegistry(ConnectorBaseImageClass, [])
        raw_entries = json.loads(dump_path.read_text())
        return VersionRegistry(ConnectorBaseImageClass, [RegistryEntry.from_dict(raw_entry) for raw_entry in raw_entries])

    def save(self):
        """Writes the registry to disk. The registry is dumped as a json file with a list of RegistryEntry objects."""
        as_json = json.dumps([entry.to_serializable_dict() for entry in self.entries])
        self.dump_path.write_text(as_json)

    def add_entry(self, new_entry: RegistryEntry) -> List[RegistryEntry]:
        """Registers a new entry in the registry.

        Args:
            new_entry (RegistryEntry): The new entry to register.

        Returns:
            List[RegistryEntry]: All the entries sorted by version number in descending order.
        """
        self._entries.append(new_entry)
        return self.entries

    @property
    def entries(self) -> List[RegistryEntry]:
        """Returns all the base image versions sorted by version number in descending order.

        Returns:
            List[Type[RegistryEntry]]: All the published versions sorted by version number in descending order.
        """
        return sorted(self._entries, key=lambda entry: entry.version, reverse=True)

    @property
    def latest_version(self) -> Optional[semver.VersionInfo]:
        """Returns the latest published version in this registry.
        If no version is published, returns None.
        Returns:
            Optional[semver.VersionInfo]: The latest published version in this registry.
        """
        try:
            return self.entries[0].version
        except IndexError:
            return None

    @property
    def latest_not_pre_released_address(self) -> Optional[str]:
        """Returns the address of the latest published version in this registry, if it is not a pre-release.
        Useful for upgrading connectors to the latest version.
        Returns:
            Optional[str]: The address of the latest published version in this registry, if it is not a pre-release.
        """
        try:
            not_pre_release_entries = [entry for entry in self.entries if not entry.version.prerelease]
            return not_pre_release_entries[0].published_docker_image.address
        except IndexError:
            return None


class GlobalRegistry:
    """A registry that contains all the base image versions for all the languages."""

    def __init__(self, all_registries: List[VersionRegistry]) -> None:
        self.all_registries = all_registries
        self.all_entries = [entry for registry in all_registries for entry in registry.entries]

    def get_image_address_from_image_name(self, image_name_with_tag: str) -> str:
        """Returns the address of a base image from its name with tag.
        The image address is the unique identifier of a base image thanks to its sha256 hash.

        Args:
            image_name_with_tag (str): The name of the base image with its tag.

        Raises:
            errors.BaseImageVersionNotFoundError: If the base image version is not found in the global registry.

        Returns:
            str: The address of the base image.
        """
        matching_entry = None
        for entry in self.all_entries:
            if entry.published_docker_image.name_with_tag == image_name_with_tag:
                matching_entry = entry
                break
        if matching_entry is None:
            raise errors.BaseImageVersionNotFoundError(f"Could not find base image version {image_name_with_tag} in the global registry.")
        return matching_entry.published_docker_image.address


MANAGED_BASE_IMAGES = [
    AirbytePythonConnectorBaseImage,
]  # AirbyteJavaConnectorBaseImage,]
PYTHON_REGISTRY = VersionRegistry.load_from_disk(AirbytePythonConnectorBaseImage)
GLOBAL_REGISTRY = GlobalRegistry(
    [
        PYTHON_REGISTRY,
    ]
)  # ,  java.VERSION_REGISTRY])

CONNECTOR_LANGUAGE_LATEST_BASE_IMAGE_ADDRESSES = {
    ConnectorLanguage.PYTHON: PYTHON_REGISTRY.latest_not_pre_released_address,
    ConnectorLanguage.LOW_CODE: PYTHON_REGISTRY.latest_not_pre_released_address,
    # ConnectorLanguage.JAVA: LATEST_JAVA_BASE_IMAGE_ADDRESS,
}
