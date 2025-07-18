#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares common (abstract) classes and methods used by all base images."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import final

import semver

from .published_image import PublishedImage


class AirbyteConnectorBaseImage(ABC):
    """An abstract class that represents an Airbyte base image.
    Please do not declare any Dagger with_exec instruction in this class as in the abstract class context we have no guarantee about the underlying system used in the base image.
    """

    USER: str = "airbyte"
    USER_ID: int = 1000
    CACHE_DIR_PATH: str = "/custom_cache"
    AIRBYTE_DIR_PATH: str = "/airbyte"

    @final
    def __init__(self, version: semver.VersionInfo):
        """Initializes the Airbyte base image.

        Args:
            version (semver.VersionInfo): The version of the base image.
        """
        self.version = version

    # INSTANCE PROPERTIES:

    @property
    def name_with_tag(self) -> str:
        """Returns the full name of the Airbyte base image, with its tag.

        Returns:
            str: The full name of the Airbyte base image, with its tag.
        """
        return f"{self.repository}:{self.version}"

    # Child classes should define their root image if the image is indeed managed by base_images.
    @property
    def root_image(self) -> PublishedImage:
        """Returns the base image used to build the Airbyte base image.

        Raises:
            NotImplementedError: Raised if a subclass does not define a 'root_image' attribute.

        Returns:
            PublishedImage: The base image used to build the Airbyte base image.
        """
        raise NotImplementedError("Subclasses must define a 'root_image' attribute.")

    # MANDATORY SUBCLASSES ATTRIBUTES / PROPERTIES:

    @property
    @abstractmethod
    def repository(self) -> str:
        """This is the name of the repository where the image will be hosted.
        e.g: airbyte/python-connector-base

        Raises:
            NotImplementedError: Raised if a subclass does not define an 'repository' attribute.

        Returns:
            str: The repository name where the image will be hosted.
        """
        raise NotImplementedError("Subclasses must define an 'repository' attribute.")

    # MANDATORY SUBCLASSES METHODS:

    @abstractmethod
    def get_container(self, platform: str) -> str:
        """Returns the image name of the Airbyte connector base image."""
        raise NotImplementedError("Subclasses must define a 'get_container' method.")

    @abstractmethod
    async def run_sanity_checks(self, platform: str):
        """Runs sanity checks on the base image container.
        This method is called before image publication.

        Args:
            platform (str): The platform on which the sanity checks should run.

        Raises:
            SanityCheckError: Raised if a sanity check fails.
        """
        raise NotImplementedError("Subclasses must define a 'run_sanity_checks' method.")

    # INSTANCE METHODS:
    @final
    def get_base_container(self, platform: str) -> str:
        """Returns the base image name.
        This is used to build the Airbyte base image using Docker.

        Returns:
            str: The base image name.
        """
        return self.root_image.address
