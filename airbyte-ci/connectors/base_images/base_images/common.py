#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares common (abstract) classes and methods used by all base images."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, final

import dagger
import semver
from connector_ops.utils import ConnectorLanguage  # type: ignore


@dataclass
class PublishedDockerImage:
    registry: str
    image_name: str
    tag: str
    sha: str

    @property
    def address(self) -> str:
        return f"{self.registry}/{self.image_name}:{self.tag}@sha256:{self.sha}"

    @staticmethod
    def from_address(address: str):
        parts = address.split("/")
        repository = parts.pop(0)
        without_repository = "/".join(parts)
        image_name, tag, sha = without_repository.replace("@sha256", "").split(":")
        return PublishedDockerImage(repository, image_name, tag, sha)

    @property
    def name_with_tag(self) -> str:
        return f"{self.image_name}:{self.tag}"


class AirbyteConnectorBaseImage(ABC):
    """An abstract class that represents an Airbyte base image.
    Please do not declare any Dagger with_exec instruction in this class as in the abstract class context we have no guarantee about the underlying system used in the base image.
    """

    @final
    def __init__(self, dagger_client: dagger.Client, version: semver.VersionInfo):
        """Initializes the Airbyte base image.

        Args:
            dagger_client (dagger.Client): The dagger client used to build the base image.
            version (semver.VersionInfo): The version of the base image.
        """
        self.dagger_client = dagger_client
        self.version = version

    # INSTANCE PROPERTIES:

    @property
    def name_with_tag(self) -> str:
        """Returns the full name of the Airbyte base image, with its tag.

        Returns:
            str: The full name of the Airbyte base image, with its tag.
        """
        return f"{self.image_name}:{self.version}"

    # MANDATORY SUBCLASSES ATTRIBUTES / PROPERTIES:

    @property
    @abstractmethod
    def compatible_languages(cls) -> Tuple[ConnectorLanguage, ...]:
        """Returns connector languages compatible with this base image.

        Raises:
            NotImplementedError: Raised if a subclass does not define a 'compatible_languages' attribute.

        Returns:
            List[ConnectorLanguage]: The connector languages compatible with this base image.
        """
        raise NotImplementedError("Subclasses must define a 'compatible_languages' attribute.")

    @property
    @abstractmethod
    def base_base_image(cls) -> PublishedDockerImage:
        """Returns the base image used to build the Airbyte base image.

        Raises:
            NotImplementedError: Raised if a subclass does not define a 'base_base_image' attribute.

        Returns:
            PublishedDockerImage: The base image used to build the Airbyte base image.
        """
        raise NotImplementedError("Subclasses must define a 'base_base_image' attribute.")

    @property
    @abstractmethod
    def image_name(cls) -> str:
        """This is the name of the final base image. By name we mean image repository name (without the tag).

        Raises:
            NotImplementedError: Raised if a subclass does not define an 'image_name' attribute.

        Returns:
            str: The name of the final base image.
        """
        raise NotImplementedError("Subclasses must define an 'image_name' attribute.")

    # MANDATORY SUBCLASSES METHODS:

    @abstractmethod
    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container of the Airbyte connector base image."""
        raise NotImplementedError("Subclasses must define a 'get_container' method.")

    @abstractmethod
    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the base image container.
        This method is called before image publication.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            SanityCheckError: Raised if a sanity check fails.
        """
        raise NotImplementedError("Subclasses must define a 'run_sanity_checks' method.")

    # INSTANCE METHODS:
    @final
    def get_base_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns a container using the base image. This container is used to build the Airbyte base image.

        Returns:
            dagger.Container: The container using the base python image.
        """
        return self.dagger_client.pipeline(self.name_with_tag).container(platform=platform).from_(self.base_base_image.address)
