#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import final

import dagger
import semver
from base_images import consts


@dataclass
class PlatformAwareDockerImage:
    image_name: str
    tag: str
    sha: str
    platform: dagger.Platform

    def get_full_image_name(self) -> str:
        return f"{self.image_name}:{self.tag}@sha256:{self.sha}"


class BaseImageVersionError(ValueError):
    """Raised when the version is not in the expected format."""

    pass


class SanityCheckError(Exception):
    """Raised when a sanity check fails."""

    pass


class PlatformAvailabilityError(ValueError):
    """Raised when the platform is not supported by an image."""

    pass


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
        """Returns the base image used to build the Airbyte base image."""
        raise NotImplementedError("Subclasses must define a 'base_base_image'.")

    @property
    @abstractmethod
    def image_name(cls) -> str:
        """This is the name of the final base image."""
        raise NotImplementedError("Subclasses must define an 'image_name'.")

    @property
    @abstractmethod
    def changelog(cls) -> str:
        raise NotImplementedError("Subclasses must define a 'changelog' attribute.")

    @final
    def __init__(self, dagger_client: dagger.Client, platform: dagger.Platform):
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
        """Validates that the version is in the format `x.y.z` and each part is a digit.

        Raises:
            VersionError: Raised if the version is not in the format `x.y.z` or if any part is not a digit.
        """
        try:
            semver.VersionInfo.parse(cls.version)
        except ValueError as e:
            raise BaseImageVersionError(f"The version class {cls.__name__} is not in the expected semver format: e.g `_0_1_0`.") from e

    @final
    def _validate_platform_availability(self):
        """Validates that the platform is supported by the base image.

        Raises:
            ValueError: Raised if the platform is not supported by the base image.
        """
        if self.platform not in self.base_base_image.value:
            raise PlatformAvailabilityError(f"Platform {self.platform} is not supported by {self.base_base_image.name}.")

    @final
    @property
    def base_base_image_name(self) -> str:
        return self.base_base_image.value[self.platform].get_full_image_name()

    @property
    @final
    def base_container(self) -> dagger.Container:
        """Returns a container using the base python image. This container is used to build the Airbyte base image.
        We set environment variables and labels to ensure we can easily check:
         - the Python base image that was used to build the Airbyte base image
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

    async def run_sanity_checks(self):
        """Runs sanity checks on the base image container.
        This method is called on base image build.

        Raises:
            SanityCheckError: Raised if a sanity check fails.
        """
        if not await self.container.env_variable("AIRBYTE_BASE_BASE_IMAGE") == self.base_base_image_name:
            raise SanityCheckError("the AIRBYTE_BASE_BASE_IMAGE environment variable is not set correctly.")
        if not await self.container.env_variable("AIRBYTE_BASE_IMAGE") == self.name_with_tag:
            raise SanityCheckError("the AIRBYTE_BASE_IMAGE environment variable is not set correctly.")
        if not await self.container.label("io.airbyte.base_base_image") == self.base_base_image_name:
            raise SanityCheckError("the io.airbyte.base_base_image label is not set correctly.")
        if not await self.container.label("io.airbyte.base_image") == self.name_with_tag:
            raise SanityCheckError("the io.airbyte.base_image label is not set correctly.")

    @staticmethod
    def get_github_url(cls):
        absolute_module_path = inspect.getfile(cls)
        relative_module_path = Path(absolute_module_path).relative_to(consts.AIRBYTE_ROOT_DIR)
        # This url will resolve once the code is pushed to the main branch
        return f"{consts.AIRBYTE_GITHUB_REPO_URL}/blob/{consts.MAIN_BRANCH_NAME}/{relative_module_path}"
