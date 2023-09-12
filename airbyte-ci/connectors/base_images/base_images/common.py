#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares common (abstract) classes and methods used by all base images.
It's not meant to be regurlarly modified.
"""
from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import final

import dagger
import semver
from base_images import consts, errors


@dataclass
class PlatformAwareDockerImage:
    image_name: str
    tag: str
    sha: str
    platform: dagger.Platform

    def get_full_image_name(self) -> str:
        return f"{self.image_name}:{self.tag}@sha256:{self.sha}"


class BaseBaseImage(Enum):
    pass


class AirbyteConnectorBaseImage(ABC):
    """An abstract class that represents an Airbyte base image.
    Please do not declare any Dagger with_exec instruction in this class as in the abstract class context we have no guarantee about the underlying system used in the base image.
    """

    name_with_tag: str
    github_url: str
    version: str

    @property
    @abstractmethod
    def base_base_image(cls) -> BaseBaseImage:
        """Returns the base image used to build the Airbyte base image.

        Raises:
            NotImplementedError: Raised if a subclass does not define a 'base_base_image' attribute.

        Returns:
            BaseBaseImage: The base image used to build the Airbyte base image.
        """
        raise NotImplementedError("Subclasses must define a 'base_base_image'.")

    @property
    @abstractmethod
    def image_name(cls) -> str:
        """This is the name of the final base image. By name we mean DockerHub image name without the tag.

        Raises:
            NotImplementedError: Raised if a subclass does not define an 'image_name' attribute.

        Returns:
            str: The name of the final base image.
        """
        raise NotImplementedError("Subclasses must define an 'image_name'.")

    @property
    @abstractmethod
    def changelog_entry(cls) -> str:
        """This is the changelog entry for a new base image version.
        It will automatically be used to generate the changelog entry for the release notes.

        Raises:
            NotImplementedError: Raised if a subclass does not define a 'changelog_entry' attribute.

        Returns:
            str: The changelog entry for a new base image version.
        """
        raise NotImplementedError("Subclasses must define a 'changelog_entry' attribute.")

    @final
    def __init__(self, dagger_client: dagger.Client, platform: dagger.Platform):
        """Initializes the Airbyte base image.

        Args:
            dagger_client (dagger.Client): The dagger client used to build the base image.
            platform (dagger.Platform): The platform used to build the base image.
        """
        self.dagger_client = dagger_client
        self.platform = platform
        self._validate_platform_availability()

    @final
    def __init_subclass__(cls) -> None:
        cls.github_url = AirbyteConnectorBaseImage.get_github_url(cls)
        cls.version = AirbyteConnectorBaseImage.get_version_from_class_name(cls)
        if not inspect.isabstract(cls):
            AirbyteConnectorBaseImage._validate_version(cls)
            cls.name_with_tag = f"{cls.image_name}:{cls.version}"
        return super().__init_subclass__()

    @final
    @staticmethod
    def get_version_from_class_name(cls):
        """The version is parsed from the class name.

        Returns:
            str: The tag in the format `x.y.z`.
        """
        return ".".join(cls.__name__.replace("__", "-").split("_")[1:])

    @final
    @staticmethod
    def _validate_version(cls):
        """Validate the version follows semantic versioning naming.

        Raises:
            VersionError: Raised if the version is not following semantic versioning naming.
        """
        try:
            semver.VersionInfo.parse(cls.version)
        except ValueError as e:
            raise errors.BaseImageVersionError(
                f"The version class {cls.__name__} is not in the expected semantic versioning naming format: e.g `_0_1_0`."
            ) from e

    @final
    def _validate_platform_availability(self):
        """Validates that the base image supports the platform passed at initialization.

        Raises:
            ValueError: Raised if the platform is not supported by the base image.
        """
        if self.platform not in self.base_base_image.value:
            raise errors.PlatformAvailabilityError(f"Platform {self.platform} is not supported by {self.base_base_image.name}.")

    @final
    @property
    def base_base_image_name(self) -> str:
        """Returns the full name of the base's base image used to build the Airbyte base image.
        In this context the base's base image name contains the tag.
        Returns:
            str: The full name of the base's base image used to build the Airbyte base image, with its tag.
        """
        return self.base_base_image.value[self.platform].get_full_image_name()

    @property
    @final
    def base_container(self) -> dagger.Container:
        """Returns a container using the base python image. This container is used to build the Airbyte base image.
        We set environment variables and labels to ensure we can easily check at post build time:
         - the base image that was used to build the Airbyte base image
         - the version of the Airbyte base image

        Returns:
            dagger.Container: The container using the base python image.
        """
        return (
            self.dagger_client.container()
            .from_(self.base_base_image_name)
            .with_env_variable("AIRBYTE_BASE_BASE_IMAGE", self.base_base_image_name)
            .with_env_variable("AIRBYTE_BASE_IMAGE", self.name_with_tag)
            .with_label("io.airbyte.base_base_image", self.base_base_image_name)
            .with_label("io.airbyte.base_image", self.name_with_tag)
        )

    @property
    @abstractmethod
    def container(self) -> dagger.Container:
        """Returns a container of the Airbyte connector base image. This is where version specific definitions, like with_exec, should occur."""
        raise NotImplementedError("Subclasses must define a 'container' property.")

    async def run_sanity_checks_for_version(self):
        """Runs sanity checks on the base image container.
        This method is called on base image build.
        The following sanity checks are meant to check that labels and environment variables about the base's base image and the current Airbyte base image are correctly set.

        Raises:
            SanityCheckError: Raised if a sanity check fails.
        """
        await self.run_sanity_checks(self)

    @staticmethod
    async def run_sanity_checks(base_image_version: AirbyteConnectorBaseImage):
        """Runs sanity checks on the base image container.
        This method is called on base image build.
        This method is static to allow running sanity checks of a specific version from another one.
        The following sanity checks are meant to check that labels and environment variables about the base's base image and the current Airbyte base image are correctly set.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            SanityCheckError: Raised if a sanity check fails.
        """
        if not await base_image_version.container.env_variable("AIRBYTE_BASE_BASE_IMAGE") == base_image_version.base_base_image_name:
            raise errors.SanityCheckError("the AIRBYTE_BASE_BASE_IMAGE environment variable is not correctly set.")
        if not await base_image_version.container.env_variable("AIRBYTE_BASE_IMAGE") == base_image_version.name_with_tag:
            raise errors.SanityCheckError("the AIRBYTE_BASE_IMAGE environment variable is not correctly. set")
        if not await base_image_version.container.label("io.airbyte.base_base_image") == base_image_version.base_base_image_name:
            raise errors.SanityCheckError("the io.airbyte.base_base_image label is not correctly set.")
        if not await base_image_version.container.label("io.airbyte.base_image") == base_image_version.name_with_tag:
            raise errors.SanityCheckError("the io.airbyte.base_image label is not correctly set.")

    @staticmethod
    def get_github_url(cls) -> str:
        """This method returns the GitHub URL of the file where the class is defined on the main branch.
        This URL is used to generate the changelog entry for the release notes.
        This URL will resolve once the code is pushed to the main branch.

        Returns:
            str: The GitHub URL of the file where the class is defined on the main branch.
        """
        absolute_module_path = inspect.getfile(cls)
        relative_module_path = Path(absolute_module_path).relative_to(consts.AIRBYTE_ROOT_DIR)
        return f"{consts.AIRBYTE_GITHUB_REPO_URL}/blob/{consts.MAIN_BRANCH_NAME}/{relative_module_path}"
